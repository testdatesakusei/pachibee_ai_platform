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


def judge_trend(avg4, avg12):
    r = safe_div(avg4, avg12)
    if r is None:
        return "不明"
    if r >= 1.10:
        return "上昇"
    if r >= 1.03:
        return "微増"
    if r >= 0.97:
        return "横ばい"
    if r >= 0.90:
        return "微減"
    return "下降"


def judge_life(data_count, peak_ratio, trend, days_since_last_seen):
    if pd.isna(data_count):
        return "不明"
    if days_since_last_seen > 28:
        return "準現役"
    if data_count <= 4:
        return "導入直後"
    if data_count <= 12:
        return "導入初期"
    if peak_ratio is None or pd.isna(peak_ratio):
        return "不明"
    if peak_ratio >= 0.85 and trend in ["上昇", "微増", "横ばい"]:
        return "高稼働期"
    if peak_ratio >= 0.65:
        return "成熟期"
    if peak_ratio >= 0.40:
        return "下降期"
    return "撤去検討期"


def main():
    conn = sqlite3.connect(DB_PATH)

    print("feature_05_lifecycle 作成開始 active版")

    latest = pd.read_sql("SELECT * FROM feature_01_latest", conn)
    avg = pd.read_sql("SELECT * FROM feature_02_average", conn)
    peak = pd.read_sql("SELECT * FROM feature_03_peak", conn)

    df = latest.merge(
        avg.drop(columns=["machine_name"], errors="ignore"),
        on="machine_id",
        how="left",
    ).merge(
        peak.drop(columns=["machine_name"], errors="ignore"),
        on="machine_id",
        how="left",
    )

    for col in ["avg_out_4w", "avg_out_12w", "latest_out_per_unit", "peak_ratio_out"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    rows = []

    for _, r in df.iterrows():
        trend = judge_trend(r["avg_out_4w"], r["avg_out_12w"])
        life_stage = judge_life(
            r["data_count"],
            r["peak_ratio_out"],
            trend,
            r["days_since_last_seen"],
        )

        change_4w_vs_12w = safe_div(r["avg_out_4w"] - r["avg_out_12w"], r["avg_out_12w"])

        if life_stage in ["高稼働期", "成熟期"]:
            life_score = 90
        elif life_stage == "導入初期":
            life_score = 80
        elif life_stage == "導入直後":
            life_score = 70
        elif life_stage == "下降期":
            life_score = 45
        elif life_stage == "撤去検討期":
            life_score = 20
        elif life_stage == "準現役":
            life_score = 30
        else:
            life_score = 50

        rows.append({
            "machine_id": r["machine_id"],
            "machine_name": r["machine_name"],
            "trend": trend,
            "life_stage": life_stage,
            "life_score": life_score,
            "change_rate_4w_vs_12w": change_4w_vs_12w,
            "peak_ratio_out": r["peak_ratio_out"],
            "days_since_last_seen": r["days_since_last_seen"],
            "data_count": r["data_count"],
        })

    out_df = pd.DataFrame(rows)

    conn.execute("DROP TABLE IF EXISTS feature_05_lifecycle")
    out_df.to_sql("feature_05_lifecycle", conn, if_exists="replace", index=False)

    conn.commit()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = OUTPUT_DIR / "feature_05_lifecycle.csv"
    out_df.to_csv(out_csv, index=False, encoding="utf-8-sig")

    print("作成完了")
    print(f"件数: {len(out_df)}")
    print(f"CSV出力: {out_csv}")
    print(
        out_df.sort_values("life_score", ascending=False)
        .head(30)
        .to_string(index=False)
    )

    conn.close()


if __name__ == "__main__":
    main()