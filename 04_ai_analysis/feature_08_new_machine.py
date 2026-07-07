# -*- coding: utf-8 -*-
from __future__ import annotations

import sqlite3
from pathlib import Path
import pandas as pd

BASE_DIR = Path(r"C:\Users\otsuk\Desktop\pachibee_ai_platform")
DB_PATH = BASE_DIR / "09_database" / "ai_platform.db"
OUTPUT_DIR = BASE_DIR / "output" / "features"


def judge_new_machine(row):
    if row["data_count"] > 20:
        return "対象外"
    if row["avg_out_4w"] >= 25000:
        return "期待以上"
    if row["avg_out_4w"] >= 18000:
        return "良好"
    if row["avg_out_4w"] >= 12000:
        return "標準"
    if row["avg_out_4w"] >= 8000:
        return "弱い"
    return "厳しい"


def main():
    conn = sqlite3.connect(DB_PATH)

    print("feature_08_new_machine 作成開始 active版")

    latest = pd.read_sql("SELECT * FROM feature_01_latest", conn)
    avg = pd.read_sql("SELECT * FROM feature_02_average", conn)
    market = pd.read_sql("SELECT * FROM feature_04_market", conn)
    trend = pd.read_sql("SELECT * FROM feature_06_trend", conn)

    df = latest.merge(
        avg.drop(columns=["machine_name"], errors="ignore"),
        on="machine_id",
        how="left",
    ).merge(
        market[["machine_id", "market_power_score", "market_power_band"]],
        on="machine_id",
        how="left",
    ).merge(
        trend[["machine_id", "trend_score", "trend_strength"]],
        on="machine_id",
        how="left",
    )

    for col in ["avg_out_4w", "avg_sales_4w", "avg_profit_4w", "market_power_score", "trend_score"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["is_new_machine"] = (df["data_count"] <= 20).astype(int)
    df["new_machine_judge"] = df.apply(judge_new_machine, axis=1)

    df["new_machine_score"] = (
        df["avg_out_4w"].rank(pct=True) * 45
        + df["avg_sales_4w"].rank(pct=True) * 25
        + df["avg_profit_4w"].rank(pct=True) * 15
        + df["market_power_score"].fillna(50) * 0.10
        + df["trend_score"].fillna(50) * 0.05
    ).round(1)

    df.loc[df["is_new_machine"] == 0, "new_machine_score"] = None

    out_cols = [
        "machine_id",
        "machine_name",
        "latest_data_date",
        "data_count",
        "is_new_machine",
        "avg_out_4w",
        "avg_sales_4w",
        "avg_profit_4w",
        "market_power_score",
        "trend_score",
        "trend_strength",
        "new_machine_score",
        "new_machine_judge",
    ]

    out_df = df[out_cols].copy()

    conn.execute("DROP TABLE IF EXISTS feature_08_new_machine")
    out_df.to_sql("feature_08_new_machine", conn, if_exists="replace", index=False)

    conn.commit()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = OUTPUT_DIR / "feature_08_new_machine.csv"
    out_df.to_csv(out_csv, index=False, encoding="utf-8-sig")

    print("作成完了")
    print(f"件数: {len(out_df)}")
    print(f"CSV出力: {out_csv}")
    print(
        out_df[out_df["is_new_machine"] == 1]
        .sort_values("new_machine_score", ascending=False)
        .head(30)
        .to_string(index=False)
    )

    conn.close()


if __name__ == "__main__":
    main()