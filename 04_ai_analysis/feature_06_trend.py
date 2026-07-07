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


def judge_trend_score(rate_4w, rate_12w, volatility):
    score = 50

    if rate_4w is not None:
        score += rate_4w * 120

    if rate_12w is not None:
        score += rate_12w * 80

    if volatility is not None:
        score -= volatility * 40

    if score > 100:
        score = 100
    if score < 0:
        score = 0

    return round(score, 1)


def main():
    conn = sqlite3.connect(DB_PATH)

    print("feature_06_trend 作成開始 active版")

    df = pd.read_sql("""
        SELECT
            w.data_date,
            w.machine_id,
            a.machine_name,
            w.out_per_unit
        FROM weekly_machine_data w
        INNER JOIN active_machine_master a
            ON w.machine_id = a.machine_id
        WHERE w.machine_id IS NOT NULL
          AND LOWER(w.machine_name_normalized) != 'nan'
        ORDER BY w.machine_id, w.data_date
    """, conn)

    df["data_date"] = pd.to_datetime(df["data_date"])
    df["out_per_unit"] = pd.to_numeric(df["out_per_unit"], errors="coerce")

    rows = []

    for machine_id, g in df.groupby("machine_id"):
        g = g.sort_values("data_date").copy()
        machine_name = g["machine_name"].iloc[-1]

        latest_out = g["out_per_unit"].iloc[-1]

        avg_4w = g.tail(4)["out_per_unit"].mean()
        avg_8w = g.tail(8)["out_per_unit"].mean()
        avg_12w = g.tail(12)["out_per_unit"].mean()
        avg_26w = g.tail(26)["out_per_unit"].mean()

        prev_4w = g.iloc[-8:-4]["out_per_unit"].mean() if len(g) >= 8 else None
        prev_12w = g.iloc[-24:-12]["out_per_unit"].mean() if len(g) >= 24 else None

        rate_4w = safe_div(avg_4w - prev_4w, prev_4w) if prev_4w is not None else None
        rate_12w = safe_div(avg_12w - prev_12w, prev_12w) if prev_12w is not None else None
        rate_4w_vs_26w = safe_div(avg_4w - avg_26w, avg_26w)

        volatility_12w = safe_div(g.tail(12)["out_per_unit"].std(), avg_12w)
        volatility_26w = safe_div(g.tail(26)["out_per_unit"].std(), avg_26w)

        trend_score = judge_trend_score(rate_4w, rate_12w, volatility_12w)

        if trend_score >= 75:
            trend_strength = "強い上昇"
        elif trend_score >= 60:
            trend_strength = "上昇"
        elif trend_score >= 45:
            trend_strength = "横ばい"
        elif trend_score >= 30:
            trend_strength = "下降"
        else:
            trend_strength = "強い下降"

        rows.append({
            "machine_id": machine_id,
            "machine_name": machine_name,
            "latest_out_per_unit": latest_out,
            "avg_out_4w": avg_4w,
            "avg_out_8w": avg_8w,
            "avg_out_12w": avg_12w,
            "avg_out_26w": avg_26w,
            "trend_rate_4w": rate_4w,
            "trend_rate_12w": rate_12w,
            "trend_rate_4w_vs_26w": rate_4w_vs_26w,
            "volatility_12w": volatility_12w,
            "volatility_26w": volatility_26w,
            "trend_score": trend_score,
            "trend_strength": trend_strength,
        })

    out_df = pd.DataFrame(rows)

    conn.execute("DROP TABLE IF EXISTS feature_06_trend")
    out_df.to_sql("feature_06_trend", conn, if_exists="replace", index=False)

    conn.commit()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = OUTPUT_DIR / "feature_06_trend.csv"
    out_df.to_csv(out_csv, index=False, encoding="utf-8-sig")

    print("作成完了")
    print(f"件数: {len(out_df)}")
    print(f"CSV出力: {out_csv}")
    print(
        out_df.sort_values("trend_score", ascending=False)
        .head(30)
        .to_string(index=False)
    )

    conn.close()


if __name__ == "__main__":
    main()