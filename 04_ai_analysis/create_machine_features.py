# -*- coding: utf-8 -*-
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


BASE_DIR = Path(r"C:\Users\otsuk\Desktop\pachibee_ai_platform")
DB_PATH = BASE_DIR / "09_database" / "ai_platform.db"


def safe_div(a, b):
    if b is None or b == 0 or pd.isna(b):
        return None
    if a is None or pd.isna(a):
        return None
    return a / b


def judge_trend(avg4, avg12):
    ratio = safe_div(avg4, avg12)
    if ratio is None:
        return "不明"
    if ratio >= 1.10:
        return "上昇"
    if ratio >= 1.03:
        return "微増"
    if ratio >= 0.97:
        return "横ばい"
    if ratio >= 0.90:
        return "微減"
    return "下降"


def judge_life_stage(weeks, peak_ratio, trend):
    if weeks is None or pd.isna(weeks):
        return "不明"

    if weeks <= 12:
        return "導入初期"

    if peak_ratio is None or pd.isna(peak_ratio):
        return "不明"

    if peak_ratio >= 0.85 and trend in ["上昇", "微増", "横ばい"]:
        return "成長・高稼働期"

    if peak_ratio >= 0.65:
        return "成熟期"

    if peak_ratio >= 0.40:
        return "下降期"

    return "撤去検討期"


def main():
    conn = sqlite3.connect(DB_PATH)

    print("machine_features 作成開始")
    print(f"DB: {DB_PATH}")

    df = pd.read_sql(
        """
        SELECT
            w.data_date,
            w.machine_id,
            m.machine_name,
            w.out_per_unit,
            w.out_per_player,
            w.sales_per_unit,
            w.sales_per_player,
            w.gross_profit_per_unit,
            w.gross_profit_per_player,
            m.first_seen_date,
            m.last_seen_date,
            c.certification_date
        FROM weekly_machine_data w
        INNER JOIN machine_master m
            ON w.machine_id = m.machine_id
        LEFT JOIN certification_master c
            ON m.machine_name_normalized = c.machine_name
        WHERE w.machine_id IS NOT NULL
          AND LOWER(w.machine_name_normalized) != 'nan'
        ORDER BY w.machine_id, w.data_date
        """,
        conn,
    )

    df["data_date"] = pd.to_datetime(df["data_date"])
    df["first_seen_date"] = pd.to_datetime(df["first_seen_date"])
    df["last_seen_date"] = pd.to_datetime(df["last_seen_date"])

    latest_date = df["data_date"].max()
    print(f"最新データ日: {latest_date.date()}")
    print(f"対象レコード数: {len(df)}")

    features = []

    for machine_id, g in df.groupby("machine_id"):
        g = g.sort_values("data_date").copy()

        machine_name = g["machine_name"].iloc[0]
        first_seen = g["first_seen_date"].iloc[0]
        last_seen = g["last_seen_date"].iloc[0]
        certification_date = g["certification_date"].iloc[0]

        latest = g.iloc[-1]

        out_all_avg = g["out_per_unit"].mean()
        sales_all_avg = g["sales_per_unit"].mean()
        profit_all_avg = g["gross_profit_per_unit"].mean()

        out_4w = g.tail(4)["out_per_unit"].mean()
        out_12w = g.tail(12)["out_per_unit"].mean()
        out_26w = g.tail(26)["out_per_unit"].mean()
        out_52w = g.tail(52)["out_per_unit"].mean()

        sales_4w = g.tail(4)["sales_per_unit"].mean()
        sales_12w = g.tail(12)["sales_per_unit"].mean()

        profit_4w = g.tail(4)["gross_profit_per_unit"].mean()
        profit_12w = g.tail(12)["gross_profit_per_unit"].mean()

        peak_out = g["out_per_unit"].max()
        peak_row = g.loc[g["out_per_unit"].idxmax()] if pd.notna(peak_out) else None
        peak_date = peak_row["data_date"] if peak_row is not None else None

        latest_out = latest["out_per_unit"]
        peak_ratio = safe_div(latest_out, peak_out)

        weeks_from_first_seen = int((latest_date - first_seen).days // 7)
        data_weeks = len(g)

        trend = judge_trend(out_4w, out_12w)
        life_stage = judge_life_stage(weeks_from_first_seen, peak_ratio, trend)

        features.append(
            {
                "machine_id": machine_id,
                "machine_name": machine_name,

                "latest_data_date": latest_date.strftime("%Y-%m-%d"),
                "first_seen_date": first_seen.strftime("%Y-%m-%d"),
                "last_seen_date": last_seen.strftime("%Y-%m-%d"),
                "certification_date": certification_date,

                "data_weeks": data_weeks,
                "weeks_from_first_seen": weeks_from_first_seen,

                "latest_out_per_unit": latest_out,
                "avg_out_4w": out_4w,
                "avg_out_12w": out_12w,
                "avg_out_26w": out_26w,
                "avg_out_52w": out_52w,
                "avg_out_all": out_all_avg,

                "latest_sales_per_unit": latest["sales_per_unit"],
                "avg_sales_4w": sales_4w,
                "avg_sales_12w": sales_12w,
                "avg_sales_all": sales_all_avg,

                "latest_profit_per_unit": latest["gross_profit_per_unit"],
                "avg_profit_4w": profit_4w,
                "avg_profit_12w": profit_12w,
                "avg_profit_all": profit_all_avg,

                "peak_out_per_unit": peak_out,
                "peak_out_date": peak_date.strftime("%Y-%m-%d") if peak_date is not None else None,
                "peak_ratio": peak_ratio,

                "trend": trend,
                "life_stage": life_stage,
            }
        )

    feature_df = pd.DataFrame(features)

    # 市場順位
    feature_df["rank_out_4w"] = feature_df["avg_out_4w"].rank(
        ascending=False, method="min"
    )
    feature_df["rank_sales_4w"] = feature_df["avg_sales_4w"].rank(
        ascending=False, method="min"
    )
    feature_df["rank_profit_4w"] = feature_df["avg_profit_4w"].rank(
        ascending=False, method="min"
    )

    # スコア：まずは簡易版
    feature_df["operation_score"] = (
        feature_df["avg_out_4w"].rank(pct=True) * 40
        + feature_df["peak_ratio"].fillna(0).rank(pct=True) * 30
        + feature_df["avg_sales_4w"].rank(pct=True) * 20
        + feature_df["avg_profit_4w"].rank(pct=True) * 10
    ).round(1)

    conn.execute("DROP TABLE IF EXISTS machine_features")

    feature_df.to_sql(
        "machine_features",
        conn,
        if_exists="replace",
        index=False,
    )

    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_machine_features_id ON machine_features(machine_id)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_machine_features_score ON machine_features(operation_score)"
    )

    conn.commit()

    print("-" * 60)
    print("作成完了")
    print(f"machine_features 件数: {len(feature_df)}")
    print("-" * 60)

    print("稼働スコア上位20件")
    print(
        feature_df[
            [
                "machine_id",
                "machine_name",
                "avg_out_4w",
                "peak_ratio",
                "trend",
                "life_stage",
                "operation_score",
            ]
        ]
        .sort_values("operation_score", ascending=False)
        .head(20)
        .to_string(index=False)
    )

    # CSV出力
    feature_dir = BASE_DIR / "output" / "features"
    feature_dir.mkdir(parents=True, exist_ok=True)

    out_csv = feature_dir / "machine_features.csv"
    feature_df.to_csv(out_csv, index=False, encoding="utf-8-sig")
    print(f"CSV出力: {out_csv}")

    conn.close()


if __name__ == "__main__":
    main()