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

    print("market_rankings 作成開始")
    print(f"DB: {DB_PATH}")

    df = pd.read_sql(
        """
        SELECT
            machine_id,
            machine_name,
            latest_data_date,
            first_seen_date,
            last_seen_date,
            data_weeks,
            weeks_from_first_seen,

            latest_out_per_unit,
            avg_out_4w,
            avg_out_12w,
            avg_out_26w,
            avg_out_52w,

            latest_sales_per_unit,
            avg_sales_4w,
            avg_sales_12w,

            latest_profit_per_unit,
            avg_profit_4w,
            avg_profit_12w,

            peak_out_per_unit,
            peak_ratio,
            trend,
            life_stage,
            operation_score
        FROM machine_features
        """,
        conn,
    )

    # 数値化
    numeric_cols = [
        "latest_out_per_unit",
        "avg_out_4w",
        "avg_out_12w",
        "avg_out_26w",
        "avg_out_52w",
        "latest_sales_per_unit",
        "avg_sales_4w",
        "avg_sales_12w",
        "latest_profit_per_unit",
        "avg_profit_4w",
        "avg_profit_12w",
        "peak_out_per_unit",
        "peak_ratio",
        "operation_score",
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # ランキング
    df["rank_out_4w"] = df["avg_out_4w"].rank(ascending=False, method="min")
    df["rank_sales_4w"] = df["avg_sales_4w"].rank(ascending=False, method="min")
    df["rank_profit_4w"] = df["avg_profit_4w"].rank(ascending=False, method="min")
    df["rank_operation_score"] = df["operation_score"].rank(
        ascending=False, method="min"
    )

    # 市場ランク帯
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

    df["out_rank_band"] = df["rank_out_4w"].apply(rank_band)
    df["score_rank_band"] = df["rank_operation_score"].apply(rank_band)

    # 実用判断
    def market_position(row):
        score = row["operation_score"]
        trend = row["trend"]
        life = row["life_stage"]

        if pd.isna(score):
            return "判定不可"

        if score >= 90 and life in ["導入初期", "成長・高稼働期"]:
            return "主力候補"

        if score >= 80 and trend in ["上昇", "微増", "横ばい"]:
            return "準主力"

        if score >= 65:
            return "標準運用"

        if score >= 50:
            return "注意運用"

        return "撤去・売却検討"

    df["market_position"] = df.apply(market_position, axis=1)

    # DB保存
    conn.execute("DROP TABLE IF EXISTS market_rankings")

    df.to_sql(
        "market_rankings",
        conn,
        if_exists="replace",
        index=False,
    )

    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_market_rankings_machine_id ON market_rankings(machine_id)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_market_rankings_score ON market_rankings(operation_score)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_market_rankings_out_rank ON market_rankings(rank_out_4w)"
    )

    conn.commit()

    # CSV出力
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = OUTPUT_DIR / "market_rankings.csv"
    df.to_csv(out_csv, index=False, encoding="utf-8-sig")

    print("-" * 60)
    print("作成完了")
    print(f"market_rankings 件数: {len(df)}")
    print(f"CSV出力: {out_csv}")
    print("-" * 60)

    print("総合スコア上位20件")
    print(
        df[
            [
                "rank_operation_score",
                "machine_id",
                "machine_name",
                "avg_out_4w",
                "rank_out_4w",
                "trend",
                "life_stage",
                "operation_score",
                "market_position",
            ]
        ]
        .sort_values("rank_operation_score")
        .head(20)
        .to_string(index=False)
    )

    print("-" * 60)

    print("アウト4週平均 上位20件")
    print(
        df[
            [
                "rank_out_4w",
                "machine_id",
                "machine_name",
                "avg_out_4w",
                "operation_score",
                "trend",
                "life_stage",
                "market_position",
            ]
        ]
        .sort_values("rank_out_4w")
        .head(20)
        .to_string(index=False)
    )

    conn.close()


if __name__ == "__main__":
    main()