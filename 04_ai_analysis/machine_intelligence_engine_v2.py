# -*- coding: utf-8 -*-
"""
Machine Intelligence Engine v2 修正版
PachiBee AI 機種AI

修正点：
- rank計算時のNaNエラー対策
- P/S別ランキング出力
- 市場/SNS未取得データは中立評価50
"""

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]

SRC = ROOT / "output" / "machine_feature_snapshot_v1.csv"

OUT_ALL = ROOT / "output" / "machine_intelligence_v2_all.csv"
OUT_P = ROOT / "output" / "machine_intelligence_v2_P.csv"
OUT_S = ROOT / "output" / "machine_intelligence_v2_S.csv"


def safe_num(s):
    return pd.to_numeric(s, errors="coerce").replace([np.inf, -np.inf], np.nan)


def minmax_score(s):
    s = safe_num(s)
    if s.notna().sum() == 0:
        return pd.Series([50] * len(s), index=s.index)
    if s.max() == s.min():
        return pd.Series([50] * len(s), index=s.index)
    return ((s - s.min()) / (s.max() - s.min()) * 100).round(2)


def grade(score):
    if pd.isna(score):
        return "D"
    if score >= 85:
        return "S"
    if score >= 70:
        return "A"
    if score >= 55:
        return "B"
    if score >= 40:
        return "C"
    return "D"


def trend_score(latest, avg4, avg12):
    latest = safe_num(latest)
    avg4 = safe_num(avg4)
    avg12 = safe_num(avg12)

    raw = (
        (latest / avg4.replace(0, np.nan)) * 50 +
        (avg4 / avg12.replace(0, np.nan)) * 50
    )

    raw = raw.replace([np.inf, -np.inf], np.nan).fillna(50)
    return raw.clip(lower=0, upper=120).round(2)


def main():
    if not SRC.exists():
        print("machine_feature_snapshot_v1.csv がありません。先に build_machine_feature_snapshot.py を実行してください。")
        return

    df = pd.read_csv(SRC)

    # category空欄対策
    df["category"] = df["category"].fillna("UNKNOWN").astype(str)

    numeric_cols = [
        "latest_operation",
        "avg_operation_4w",
        "avg_operation_12w",
        "avg_operation_all",
        "max_operation",
        "min_operation",
        "operation_contribution_weeks",
        "latest_sales",
        "avg_sales_4w",
        "avg_sales_12w",
        "avg_sales_all",
        "latest_gross_profit",
        "avg_gross_profit_4w",
        "avg_gross_profit_12w",
        "avg_gross_profit_all",
        "profit_tolerance_score",
        "popularity_score",
        "profit_score",
        "lifecycle_score",
        "asset_score",
        "overall_score",
    ]

    for c in numeric_cols:
        if c in df.columns:
            df[c] = safe_num(df[c])

    # 欠損は計算用に0ではなく平均的な扱いへ寄せる
    for c in [
        "latest_operation",
        "avg_operation_4w",
        "avg_operation_12w",
        "avg_gross_profit_4w",
        "avg_gross_profit_12w",
        "operation_contribution_weeks",
    ]:
        if c in df.columns:
            df[c] = df[c].fillna(0)

    # -----------------------------------------
    # v2用の個別スコア
    # -----------------------------------------

    df["current_operation_score"] = minmax_score(df["avg_operation_4w"])
    df["latest_operation_score"] = minmax_score(df["latest_operation"])

    df["trend_score"] = trend_score(
        df["latest_operation"],
        df["avg_operation_4w"],
        df["avg_operation_12w"]
    )

    df["profit_power_score"] = minmax_score(df["avg_gross_profit_4w"])
    df["profit_stability_score"] = minmax_score(df["avg_gross_profit_12w"])
    df["lifecycle_power_score"] = minmax_score(df["operation_contribution_weeks"])

    # 市場・SNSはまだ未取得なので中立評価50
    df["market_power_score"] = 50
    df["sns_power_score"] = 50

    # -----------------------------------------
    # v2スコア
    # -----------------------------------------

    df["active_popularity_score_v2"] = (
        df["current_operation_score"] * 0.40 +
        df["latest_operation_score"] * 0.30 +
        df["trend_score"] * 0.15 +
        df["market_power_score"] * 0.10 +
        df["sns_power_score"] * 0.05
    ).round(2)

    df["profit_score_v2"] = (
        df["profit_power_score"] * 0.50 +
        df["profit_stability_score"] * 0.20 +
        df["current_operation_score"] * 0.20 +
        df["lifecycle_power_score"] * 0.10
    ).round(2)

    df["lifecycle_score_v2"] = (
        df["lifecycle_power_score"] * 0.45 +
        df["current_operation_score"] * 0.25 +
        df["trend_score"] * 0.20 +
        df["market_power_score"] * 0.10
    ).round(2)

    df["asset_score_v2"] = (
        df["profit_score_v2"] * 0.35 +
        df["active_popularity_score_v2"] * 0.35 +
        df["lifecycle_score_v2"] * 0.20 +
        df["market_power_score"] * 0.10
    ).round(2)

    df["overall_score_v2"] = (
        df["active_popularity_score_v2"] * 0.40 +
        df["profit_score_v2"] * 0.25 +
        df["lifecycle_score_v2"] * 0.20 +
        df["asset_score_v2"] * 0.15
    ).round(2)

    df["overall_grade_v2"] = df["overall_score_v2"].apply(grade)

    # -----------------------------------------
    # ランキング NaN対策済み
    # -----------------------------------------

    df["active_rank"] = (
        df.groupby("category")["active_popularity_score_v2"]
        .rank(method="min", ascending=False)
        .fillna(999999).astype(int)
    )

    df["profit_rank"] = (
        df.groupby("category")["profit_score_v2"]
        .rank(method="min", ascending=False)
        .fillna(999999).astype(int)
    )

    df["lifecycle_rank"] = (
        df.groupby("category")["lifecycle_score_v2"]
        .rank(method="min", ascending=False)
        .fillna(999999).astype(int)
    )

    df["overall_rank"] = (
        df.groupby("category")["overall_score_v2"]
        .rank(method="min", ascending=False)
        .fillna(999999).astype(int)
    )

    # -----------------------------------------
    # 説明文
    # -----------------------------------------

    def reason(row):
        return (
            f"直近4週稼働スコア{row['current_operation_score']:.1f} / "
            f"最新稼働スコア{row['latest_operation_score']:.1f} / "
            f"トレンドスコア{row['trend_score']:.1f} / "
            f"粗利スコア{row['profit_power_score']:.1f} / "
            f"稼働貢献スコア{row['lifecycle_power_score']:.1f} / "
            f"市場データ未取得のため中立評価 / "
            f"SNSデータ未取得のため中立評価"
        )

    df["score_reason_v2"] = df.apply(reason, axis=1)

    df["ai_comment_v2"] = df.apply(
        lambda r: (
            f"{r['machine_name']}は、現役人気指数{r['active_popularity_score_v2']:.1f}、"
            f"粗利指数{r['profit_score_v2']:.1f}、"
            f"寿命指数{r['lifecycle_score_v2']:.1f}、"
            f"総合評価{r['overall_score_v2']:.1f}（{r['overall_grade_v2']}）。"
            f"主な根拠は、{r['score_reason_v2']}。"
        ),
        axis=1
    )

    # -----------------------------------------
    # 出力
    # -----------------------------------------

    df = df.sort_values(["category", "overall_rank"])

    df.to_csv(OUT_ALL, index=False, encoding="utf-8-sig")
    df[df["category"] == "P"].to_csv(OUT_P, index=False, encoding="utf-8-sig")
    df[df["category"] == "S"].to_csv(OUT_S, index=False, encoding="utf-8-sig")

    print("作成完了")
    print(f"全体: {OUT_ALL}")
    print(f"パチンコ: {OUT_P}")
    print(f"パチスロ: {OUT_S}")
    print(f"件数: {len(df)}")
    print()
    print("パチンコ 総合上位20")
    print(
        df[df["category"] == "P"][
            [
                "overall_rank",
                "machine_name",
                "overall_score_v2",
                "active_popularity_score_v2",
                "profit_score_v2",
                "lifecycle_score_v2",
                "overall_grade_v2",
            ]
        ].head(20).to_string(index=False)
    )
    print()
    print("パチスロ 総合上位20")
    print(
        df[df["category"] == "S"][
            [
                "overall_rank",
                "machine_name",
                "overall_score_v2",
                "active_popularity_score_v2",
                "profit_score_v2",
                "lifecycle_score_v2",
                "overall_grade_v2",
            ]
        ].head(20).to_string(index=False)
    )


if __name__ == "__main__":
    main()