# -*- coding: utf-8 -*-
from __future__ import annotations

import sqlite3
from pathlib import Path
import pandas as pd

BASE_DIR = Path(r"C:\Users\otsuk\Desktop\pachibee_ai_platform")
DB_PATH = BASE_DIR / "09_database" / "ai_platform.db"
OUTPUT_DIR = BASE_DIR / "output" / "features"


def safe_div(a, b):
    if pd.isna(a) or pd.isna(b) or b == 0:
        return None
    return a / b


def main():
    conn = sqlite3.connect(DB_PATH)

    print("feature_03_peak 作成開始 active版")

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
        g = g.sort_values("data_date").copy()
        latest = g.iloc[-1]
        machine_name = latest["machine_name"]

        peak_out = g["out_per_unit"].max()
        peak_sales = g["sales_per_unit"].max()
        peak_profit = g["gross_profit_per_unit"].max()

        peak_out_date = None
        if pd.notna(peak_out):
            peak_out_date = g.loc[g["out_per_unit"].idxmax(), "data_date"]

        latest_out = latest["out_per_unit"]
        latest_sales = latest["sales_per_unit"]
        latest_profit = latest["gross_profit_per_unit"]

        rows.append({
            "machine_id": machine_id,
            "machine_name": machine_name,
            "peak_out_per_unit": peak_out,
            "peak_out_date": peak_out_date.strftime("%Y-%m-%d") if peak_out_date is not None else None,
            "peak_sales_per_unit": peak_sales,
            "peak_profit_per_unit": peak_profit,
            "peak_ratio_out": safe_div(latest_out, peak_out),
            "peak_ratio_sales": safe_div(latest_sales, peak_sales),
            "peak_ratio_profit": safe_div(latest_profit, peak_profit),
            "drop_from_peak_out": latest_out - peak_out if pd.notna(latest_out) and pd.notna(peak_out) else None,
            "drop_rate_from_peak_out": safe_div(latest_out - peak_out, peak_out) if pd.notna(latest_out) and pd.notna(peak_out) else None,
        })

    out_df = pd.DataFrame(rows)

    conn.execute("DROP TABLE IF EXISTS feature_03_peak")
    out_df.to_sql("feature_03_peak", conn, if_exists="replace", index=False)

    conn.commit()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = OUTPUT_DIR / "feature_03_peak.csv"
    out_df.to_csv(out_csv, index=False, encoding="utf-8-sig")

    print("作成完了")
    print(f"件数: {len(out_df)}")
    print(f"CSV出力: {out_csv}")
    print(
        out_df.sort_values("peak_out_per_unit", ascending=False)
        .head(30)
        .to_string(index=False)
    )

    conn.close()


if __name__ == "__main__":
    main()