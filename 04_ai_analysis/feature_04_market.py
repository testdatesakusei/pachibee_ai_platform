# -*- coding: utf-8 -*-
from __future__ import annotations

import sqlite3
from pathlib import Path
import pandas as pd

BASE_DIR = Path(r"C:\Users\otsuk\Desktop\pachibee_ai_platform")
DB_PATH = BASE_DIR / "09_database" / "ai_platform.db"
OUTPUT_DIR = BASE_DIR / "output" / "features"


def rank_band(rank):
    if pd.isna(rank):
        return "不明"
    if rank <= 10:
        return "TOP10"
    if rank <= 30:
        return "TOP30"
    if rank <= 50:
        return "TOP50"
    if rank <= 100:
        return "TOP100"
    return "圏外"


def score_band(score):
    if pd.isna(score):
        return "不明"
    if score >= 90:
        return "S"
    if score >= 80:
        return "A"
    if score >= 65:
        return "B"
    if score >= 50:
        return "C"
    return "D"


def main():
    conn = sqlite3.connect(DB_PATH)

    print("feature_04_market 作成開始 active版")

    latest = pd.read_sql("SELECT * FROM feature_01_latest", conn)
    avg = pd.read_sql("SELECT * FROM feature_02_average", conn)

    df = latest.merge(
        avg.drop(columns=["machine_name"], errors="ignore"),
        on="machine_id",
        how="left",
    )

    for col in [
        "latest_out_per_unit",
        "latest_sales_per_unit",
        "latest_profit_per_unit",
        "avg_out_4w",
        "avg_sales_4w",
        "avg_profit_4w",
    ]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["rank_latest_out"] = df["latest_out_per_unit"].rank(ascending=False, method="min")
    df["rank_latest_sales"] = df["latest_sales_per_unit"].rank(ascending=False, method="min")
    df["rank_latest_profit"] = df["latest_profit_per_unit"].rank(ascending=False, method="min")

    df["rank_out_4w"] = df["avg_out_4w"].rank(ascending=False, method="min")
    df["rank_sales_4w"] = df["avg_sales_4w"].rank(ascending=False, method="min")
    df["rank_profit_4w"] = df["avg_profit_4w"].rank(ascending=False, method="min")

    total_out = df["avg_out_4w"].sum()
    total_sales = df["avg_sales_4w"].sum()
    total_profit = df["avg_profit_4w"].sum()

    df["share_out_4w"] = df["avg_out_4w"] / total_out if total_out else None
    df["share_sales_4w"] = df["avg_sales_4w"] / total_sales if total_sales else None
    df["share_profit_4w"] = df["avg_profit_4w"] / total_profit if total_profit else None

    n = len(df)

    df["score_out_market"] = (1 - (df["rank_out_4w"] - 1) / n) * 100
    df["score_sales_market"] = (1 - (df["rank_sales_4w"] - 1) / n) * 100
    df["score_profit_market"] = (1 - (df["rank_profit_4w"] - 1) / n) * 100

    df["market_power_score"] = (
        df["score_out_market"] * 0.5
        + df["score_sales_market"] * 0.3
        + df["score_profit_market"] * 0.2
    ).round(1)

    df["out_rank_band"] = df["rank_out_4w"].apply(rank_band)
    df["market_power_band"] = df["market_power_score"].apply(score_band)

    out_cols = [
        "machine_id",
        "machine_name",
        "rank_latest_out",
        "rank_latest_sales",
        "rank_latest_profit",
        "rank_out_4w",
        "rank_sales_4w",
        "rank_profit_4w",
        "share_out_4w",
        "share_sales_4w",
        "share_profit_4w",
        "score_out_market",
        "score_sales_market",
        "score_profit_market",
        "market_power_score",
        "out_rank_band",
        "market_power_band",
    ]

    out_df = df[out_cols].copy()

    conn.execute("DROP TABLE IF EXISTS feature_04_market")
    out_df.to_sql("feature_04_market", conn, if_exists="replace", index=False)

    conn.commit()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = OUTPUT_DIR / "feature_04_market.csv"
    out_df.to_csv(out_csv, index=False, encoding="utf-8-sig")

    print("作成完了")
    print(f"件数: {len(out_df)}")
    print(f"CSV出力: {out_csv}")
    print(
        out_df.sort_values("market_power_score", ascending=False)
        .head(30)
        .to_string(index=False)
    )

    conn.close()


if __name__ == "__main__":
    main()