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

    print("feature_01_latest 作成開始 active版")

    df = pd.read_sql("""
        SELECT
            w.data_date,
            w.machine_id,
            a.machine_name,
            a.active_status,
            a.days_since_last_seen,
            a.weeks_since_last_seen,
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
        latest = g.iloc[-1]

        rows.append({
            "machine_id": machine_id,
            "machine_name": latest["machine_name"],
            "active_status": latest["active_status"],
            "latest_data_date": latest["data_date"].strftime("%Y-%m-%d"),
            "days_since_last_seen": latest["days_since_last_seen"],
            "weeks_since_last_seen": latest["weeks_since_last_seen"],
            "latest_out_per_unit": latest["out_per_unit"],
            "latest_sales_per_unit": latest["sales_per_unit"],
            "latest_profit_per_unit": latest["gross_profit_per_unit"],
            "data_count": len(g),
        })

    out_df = pd.DataFrame(rows)

    conn.execute("DROP TABLE IF EXISTS feature_01_latest")
    out_df.to_sql("feature_01_latest", conn, if_exists="replace", index=False)

    conn.commit()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = OUTPUT_DIR / "feature_01_latest.csv"
    out_df.to_csv(out_csv, index=False, encoding="utf-8-sig")

    print("作成完了")
    print(f"件数: {len(out_df)}")
    print(f"CSV出力: {out_csv}")
    print(
        out_df.sort_values("latest_data_date", ascending=False)
        .head(30)
        .to_string(index=False)
    )

    conn.close()


if __name__ == "__main__":
    main()