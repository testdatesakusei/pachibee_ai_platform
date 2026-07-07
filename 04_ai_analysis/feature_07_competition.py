# -*- coding: utf-8 -*-
from __future__ import annotations

import sqlite3
from pathlib import Path
import pandas as pd

BASE_DIR = Path(r"C:\Users\otsuk\Desktop\pachibee_ai_platform")
DB_PATH = BASE_DIR / "09_database" / "ai_platform.db"
OUTPUT_DIR = BASE_DIR / "output" / "features"


def category_name(name: str) -> str:
    s = str(name)

    if "ジャグラー" in s:
        return "ジャグラー"
    if "ハナハナ" in s or "沖ドキ" in s or "チバリヨ" in s:
        return "沖スロ"
    if "海物語" in s or "大海" in s:
        return "海"
    if "北斗" in s:
        return "北斗"
    if "エヴァ" in s or "エヴァンゲリオン" in s:
        return "エヴァ"
    if "東京喰種" in s:
        return "東京喰種"
    if "まどか" in s or "マギカ" in s:
        return "まどマギ"
    if s.startswith("L") or "スマスロ" in s:
        return "スマスロ"
    if s.startswith("e") or "スマパチ" in s:
        return "スマパチ"
    if s.startswith("P") or s.startswith("PA") or s.startswith("CR"):
        return "パチンコ"
    return "その他"


def main():
    conn = sqlite3.connect(DB_PATH)

    print("feature_07_competition 作成開始 active版")

    latest = pd.read_sql("SELECT * FROM feature_01_latest", conn)
    avg = pd.read_sql("SELECT * FROM feature_02_average", conn)

    df = latest.merge(
        avg.drop(columns=["machine_name"], errors="ignore"),
        on="machine_id",
        how="left",
    )

    df["category"] = df["machine_name"].apply(category_name)

    for col in ["avg_out_4w", "avg_sales_4w", "avg_profit_4w"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["category_rank_out_4w"] = df.groupby("category")["avg_out_4w"].rank(
        ascending=False,
        method="min",
    )
    df["category_rank_sales_4w"] = df.groupby("category")["avg_sales_4w"].rank(
        ascending=False,
        method="min",
    )
    df["category_rank_profit_4w"] = df.groupby("category")["avg_profit_4w"].rank(
        ascending=False,
        method="min",
    )

    category_size = df.groupby("category")["machine_id"].count().to_dict()
    df["category_size"] = df["category"].map(category_size)

    df["category_top_rate"] = 1 - (
        (df["category_rank_out_4w"] - 1) / df["category_size"]
    )

    df["category_power_score"] = (
        df["category_top_rate"] * 60
        + (1 - (df["category_rank_sales_4w"] - 1) / df["category_size"]) * 25
        + (1 - (df["category_rank_profit_4w"] - 1) / df["category_size"]) * 15
    ).round(1)

    out_cols = [
        "machine_id",
        "machine_name",
        "category",
        "category_size",
        "category_rank_out_4w",
        "category_rank_sales_4w",
        "category_rank_profit_4w",
        "category_top_rate",
        "category_power_score",
    ]

    out_df = df[out_cols].copy()

    conn.execute("DROP TABLE IF EXISTS feature_07_competition")
    out_df.to_sql("feature_07_competition", conn, if_exists="replace", index=False)

    conn.commit()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = OUTPUT_DIR / "feature_07_competition.csv"
    out_df.to_csv(out_csv, index=False, encoding="utf-8-sig")

    print("作成完了")
    print(f"件数: {len(out_df)}")
    print(f"CSV出力: {out_csv}")
    print(
        out_df.sort_values("category_power_score", ascending=False)
        .head(30)
        .to_string(index=False)
    )

    conn.close()


if __name__ == "__main__":
    main()