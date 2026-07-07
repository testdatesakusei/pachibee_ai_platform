# -*- coding: utf-8 -*-
from __future__ import annotations

import sqlite3
from pathlib import Path
import pandas as pd

BASE_DIR = Path(r"C:\Users\otsuk\Desktop\pachibee_ai_platform")
DB_PATH = BASE_DIR / "09_database" / "ai_platform.db"
OUTPUT_DIR = BASE_DIR / "output" / "features"


def read_table(conn, name):
    return pd.read_sql(f"SELECT * FROM {name}", conn)


def main():
    conn = sqlite3.connect(DB_PATH)

    print("feature_09_final 作成開始 active版 修正版")

    latest = read_table(conn, "feature_01_latest")
    average = read_table(conn, "feature_02_average")
    peak = read_table(conn, "feature_03_peak")
    market = read_table(conn, "feature_04_market")
    lifecycle = read_table(conn, "feature_05_lifecycle")
    trend = read_table(conn, "feature_06_trend")
    competition = read_table(conn, "feature_07_competition")
    new_machine = read_table(conn, "feature_08_new_machine")

    df = latest.copy()

    parts = [
        average,
        peak,
        market,
        lifecycle,
        trend,
        competition,
        new_machine,
    ]

    for part in parts:
        drop_cols = [
            c for c in part.columns
            if c != "machine_id" and c in df.columns
        ]
        part2 = part.drop(columns=drop_cols, errors="ignore")
        df = df.merge(part2, on="machine_id", how="left")

    for col in [
        "market_power_score",
        "life_score",
        "trend_score",
        "category_power_score",
        "peak_ratio_out",
        "avg_out_4w",
    ]:
        if col not in df.columns:
            df[col] = None
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["operation_power_score"] = (
        df["market_power_score"].fillna(50) * 0.35
        + df["life_score"].fillna(50) * 0.20
        + df["trend_score"].fillna(50) * 0.20
        + df["category_power_score"].fillna(50) * 0.15
        + (df["peak_ratio_out"].fillna(0.5) * 100) * 0.10
    ).round(1)

    def final_rank(score):
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

    df["operation_rank"] = df["operation_power_score"].apply(final_rank)

    def operation_comment(row):
        if row.get("is_new_machine", 0) == 1 and row.get("new_machine_judge", "") in ["期待以上", "良好"]:
            return "新台注目"
        if row.get("operation_rank") == "S" and row.get("life_stage", "") in ["高稼働期", "成熟期"]:
            return "主力維持"
        if row.get("operation_rank") in ["S", "A"] and row.get("trend_strength", "") in ["強い上昇", "上昇"]:
            return "増台候補"
        if row.get("operation_rank") in ["C", "D"] and row.get("life_stage", "") in ["下降期", "撤去検討期"]:
            return "撤去・売却検討"
        if row.get("life_stage", "") == "導入初期" and row.get("trend_strength", "") in ["下降", "強い下降"]:
            return "初期失速注意"
        return "標準運用"

    df["operation_comment"] = df.apply(operation_comment, axis=1)

    conn.execute("DROP TABLE IF EXISTS machine_features_active")
    df.to_sql("machine_features_active", conn, if_exists="replace", index=False)

    conn.execute("DROP TABLE IF EXISTS machine_features")
    df.to_sql("machine_features", conn, if_exists="replace", index=False)

    conn.commit()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = OUTPUT_DIR / "machine_features_active.csv"
    df.to_csv(out_csv, index=False, encoding="utf-8-sig")

    print("作成完了")
    print(f"件数: {len(df)}")
    print(f"CSV出力: {out_csv}")

    show_cols = [
        "machine_id",
        "machine_name",
        "operation_power_score",
        "operation_rank",
        "operation_comment",
        "avg_out_4w",
        "market_power_score",
        "life_stage",
        "trend_strength",
    ]

    print(
        df[show_cols]
        .sort_values("operation_power_score", ascending=False)
        .head(40)
        .to_string(index=False)
    )

    conn.close()


if __name__ == "__main__":
    main()