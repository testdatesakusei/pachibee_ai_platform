# -*- coding: utf-8 -*-
from __future__ import annotations

import sqlite3
from pathlib import Path
import pandas as pd

BASE_DIR = Path(r"C:\Users\otsuk\Desktop\pachibee_ai_platform")
DB_PATH = BASE_DIR / "09_database" / "ai_platform.db"
OUTPUT_DIR = BASE_DIR / "output" / "features"


def main():
    conn = sqlite3.connect(DB_PATH)

    print("feature_02_average 作成開始 active版")

    df = pd.read_sql("""
        SELECT
            w.data_date,
            w.machine_id,
            a.machine_name,
            w.out_per_unit,
            w.sales_per_unit,
            w.gross_profit_per_unit
        FROM weekly_machine_data w
        INNER JOIN active_machine_master a
            ON w.machine_id = a.machine_id
        WHERE w.machine_id IS NOT NULL
          AND LOWER(w.machine_name_normalized) != 'nan'
        ORDER BY w.machine_id, w.data_date
    """, conn)

    df["data_date"] = pd.to_datetime(df["data_date"])

    for col in ["out_per_unit", "sales_per_unit", "gross_profit_per_unit"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    rows = []

    for machine_id, g in df.groupby("machine_id"):
        g = g.sort_values("data_date")
        machine_name = g["machine_name"].iloc[-1]

        rows.append({
            "machine_id": machine_id,
            "machine_name": machine_name,
            "avg_out_4w": g.tail(4)["out_per_unit"].mean(),
            "avg_out_12w": g.tail(12)["out_per_unit"].mean(),
            "avg_out_26w": g.tail(26)["out_per_unit"].mean(),
            "avg_out_52w": g.tail(52)["out_per_unit"].mean(),
            "avg_out_all": g["out_per_unit"].mean(),
            "avg_sales_4w": g.tail(4)["sales_per_unit"].mean(),
            "avg_sales_12w": g.tail(12)["sales_per_unit"].mean(),
            "avg_sales_26w": g.tail(26)["sales_per_unit"].mean(),
            "avg_sales_52w": g.tail(52)["sales_per_unit"].mean(),
            "avg_sales_all": g["sales_per_unit"].mean(),
            "avg_profit_4w": g.tail(4)["gross_profit_per_unit"].mean(),
            "avg_profit_12w": g.tail(12)["gross_profit_per_unit"].mean(),
            "avg_profit_26w": g.tail(26)["gross_profit_per_unit"].mean(),
            "avg_profit_52w": g.tail(52)["gross_profit_per_unit"].mean(),
            "avg_profit_all": g["gross_profit_per_unit"].mean(),
        })

    out_df = pd.DataFrame(rows)

    conn.execute("DROP TABLE IF EXISTS feature_02_average")
    out_df.to_sql("feature_02_average", conn, if_exists="replace", index=False)

    conn.commit()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = OUTPUT_DIR / "feature_02_average.csv"
    out_df.to_csv(out_csv, index=False, encoding="utf-8-sig")

    print("作成完了")
    print(f"件数: {len(out_df)}")
    print(f"CSV出力: {out_csv}")
    print(
        out_df.sort_values("avg_out_4w", ascending=False)
        .head(30)
        .to_string(index=False)
    )

    conn.close()


if __name__ == "__main__":
    main()