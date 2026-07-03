# -*- coding: utf-8 -*-
"""
Machine Intelligence Engine v2.1

変更点：
- パチンコはパチンコ内だけで順位・グレード判定
- パチスロはパチスロ内だけで順位・グレード判定
- カテゴリ別パーセンタイルを追加
"""

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "output" / "machine_feature_snapshot_v1.csv"

OUT_ALL = ROOT / "output" / "machine_intelligence_v2_1_all.csv"
OUT_P = ROOT / "output" / "machine_intelligence_v2_1_P.csv"
OUT_S = ROOT / "output" / "machine_intelligence_v2_1_S.csv"


def safe_num(s):
    return pd.to_numeric(s, errors="coerce").replace([np.inf, -np.inf], np.nan)


def minmax_score(s):
    s = safe_num(s)
    if s.notna().sum() == 0 or s.max() == s.min():
        return pd.Series([50] * len(s), index=s.index)
    return ((s - s.min()) / (s.max() - s.min()) * 100).round(2)


def trend_score(latest, avg4, avg12):
    latest = safe_num(latest)
    avg4 = safe_num(avg4)
    avg12 = safe_num(avg12)

    raw = (
        (latest / avg4.replace(0, np.nan)) * 50 +
        (avg4 / avg12.replace(0, np.nan)) * 50
    )

    return raw.replace([np.inf, -np.inf], np.nan).fillna(50).clip(0, 120).round(2)


def percentile_grade(percentile):
    if percentile <= 3:
        return "S"
    if percentile <= 10:
        return "A"
    if percentile <= 25:
        return "B"
    if percentile <= 50:
        return "C"
    return "D"


def top_label(percentile):
    if percentile <= 1:
        return "TOP1%"
    if percentile <= 3:
        return "TOP3%"
    if percentile <= 5:
        return "TOP5%"
    if percentile <= 10:
        return "TOP10%"
    if percentile <= 20:
        return "TOP20%"
    if percentile <= 50:
        return "上位50%"
    return "下位50%"


def main():
    if not SRC.exists():
        print("machine_feature_snapshot_v1.csv がありません。")
        return

    df = pd.read_csv(SRC)
    df["category"] = df["category"].fillna("UNKNOWN").astype(str)

    numeric_cols = [
        "latest_operation",
        "avg_operation_4w",
        "avg_operation_12w",
        "avg_gross_profit_4w",
        "avg_gross_profit_12w",
        "operation_contribution_weeks",
    ]

    for c in numeric_cols:
        if c in df.columns:
            df[c] = safe_num(df[c]).fillna(0)

    df["current_operation_score"] = minmax_score(df["avg_operation_4w"])
    df["latest_operation_score"] = minmax_score(df["latest_operation"])
    df["trend_score"] = trend_score(
        df["latest_operation"],
        df["avg_operation_4w"],
        df["avg_operation_12w"],
    )

    df["profit_power_score"] = minmax_score(df["avg_gross_profit_4w"])
    df["profit_stability_score"] = minmax_score(df["avg_gross_profit_12w"])
    df["lifecycle_power_score"] = minmax_score(df["operation_contribution_weeks"])

    df["market_power_score"] = 50
    df["sns_power_score"] = 50

    df["active_popularity_score_v2_1"] = (
        df["current_operation_score"] * 0.40 +
        df["latest_operation_score"] * 0.30 +
        df["trend_score"] * 0.15 +
        df["market_power_score"] * 0.10 +
        df["sns_power_score"] * 0.05
    ).round(2)

    df["profit_score_v2_1"] = (
        df["profit_power_score"] * 0.50 +
        df["profit_stability_score"] * 0.20 +
        df["current_operation_score"] * 0.20 +
        df["lifecycle_power_score"] * 0.10
    ).round(2)

    df["lifecycle_score_v2_1"] = (
        df["lifecycle_power_score"] * 0.45 +
        df["current_operation_score"] * 0.25 +
        df["trend_score"] * 0.20 +
        df["market_power_score"] * 0.10
    ).round(2)

    df["asset_score_v2_1"] = (
        df["profit_score_v2_1"] * 0.35 +
        df["active_popularity_score_v2_1"] * 0.35 +
        df["lifecycle_score_v2_1"] * 0.20 +
        df["market_power_score"] * 0.10
    ).round(2)

    df["overall_score_v2_1"] = (
        df["active_popularity_score_v2_1"] * 0.40 +
        df["profit_score_v2_1"] * 0.25 +
        df["lifecycle_score_v2_1"] * 0.20 +
        df["asset_score_v2_1"] * 0.15
    ).round(2)

    # カテゴリ別順位
    for score_col, rank_col in [
        ("active_popularity_score_v2_1", "active_rank"),
        ("profit_score_v2_1", "profit_rank"),
        ("lifecycle_score_v2_1", "lifecycle_rank"),
        ("overall_score_v2_1", "overall_rank"),
    ]:
        df[rank_col] = (
            df.groupby("category")[score_col]
            .rank(method="min", ascending=False)
            .fillna(999999)
            .astype(int)
        )

    df["category_total_count"] = df.groupby("category")["machine_name"].transform("count")

    df["overall_percentile"] = (
        df["overall_rank"] / df["category_total_count"] * 100
    ).round(2)

    df["overall_grade_v2_1"] = df["overall_percentile"].apply(percentile_grade)
    df["overall_top_label"] = df["overall_percentile"].apply(top_label)

    df["category_rank_text"] = df.apply(
        lambda r: f"{r['category']}内 {int(r['overall_rank'])}位 / {int(r['category_total_count'])}機種",
        axis=1
    )

    df["score_reason_v2_1"] = df.apply(
        lambda r: (
            f"{r['category_rank_text']}。"
            f"カテゴリ内上位{r['overall_percentile']:.2f}%（{r['overall_top_label']}）。"
            f"直近4週稼働スコア{r['current_operation_score']:.1f}、"
            f"最新稼働スコア{r['latest_operation_score']:.1f}、"
            f"粗利スコア{r['profit_power_score']:.1f}、"
            f"稼働貢献スコア{r['lifecycle_power_score']:.1f}。"
        ),
        axis=1
    )

    df["ai_comment_v2_1"] = df.apply(
        lambda r: (
            f"{r['machine_name']}は{r['category_rank_text']}、"
            f"{r['overall_top_label']}評価。"
            f"現役人気指数{r['active_popularity_score_v2_1']:.1f}、"
            f"粗利指数{r['profit_score_v2_1']:.1f}、"
            f"寿命指数{r['lifecycle_score_v2_1']:.1f}、"
            f"総合評価{r['overall_score_v2_1']:.1f}。"
            f"パチンコ・パチスロを混在させず、{r['category']}カテゴリ内のみで評価。"
        ),
        axis=1
    )

    df = df.sort_values(["category", "overall_rank"])

    df.to_csv(OUT_ALL, index=False, encoding="utf-8-sig")
    df[df["category"] == "P"].to_csv(OUT_P, index=False, encoding="utf-8-sig")
    df[df["category"] == "S"].to_csv(OUT_S, index=False, encoding="utf-8-sig")

    print("作成完了")
    print(f"件数: {len(df)}")
    print()
    print("パチンコ 総合上位20")
    print(
        df[df["category"] == "P"][
            [
                "overall_rank",
                "machine_name",
                "overall_score_v2_1",
                "overall_percentile",
                "overall_top_label",
                "overall_grade_v2_1",
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
                "overall_score_v2_1",
                "overall_percentile",
                "overall_top_label",
                "overall_grade_v2_1",
            ]
        ].head(20).to_string(index=False)
    )


if __name__ == "__main__":
    main()