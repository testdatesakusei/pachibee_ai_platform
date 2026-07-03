# -*- coding: utf-8 -*-
"""
Machine Intelligence Engine v1.1
- P/S分類を補正
- ランキングをP/S別に出力
"""

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]

PERFORMANCE_CSV = ROOT / "output" / "weekly_performance_import.csv"
MASTER_CSV = ROOT / "output" / "machine_master_v2.csv"

OUT_ALL = ROOT / "output" / "machine_carte_ai_v1_1_all.csv"
OUT_P = ROOT / "output" / "machine_carte_ai_v1_1_P.csv"
OUT_S = ROOT / "output" / "machine_carte_ai_v1_1_S.csv"


def fix_category(machine_name, current_category):
    name = str(machine_name)

    p_prefixes = ("P", "PA", "PF", "e", "CR", "CRA", "ぱちんこ", "パチンコ")
    s_prefixes = ("L", "S", "スマスロ", "パチスロ")

    if name.startswith(p_prefixes):
        return "P"

    if name.startswith(s_prefixes):
        return "S"

    p_keywords = [
        "海物語", "大海", "沖海", "牙狼", "北斗無双",
        "真・北斗無双", "エヴァンゲリオン", "フィーバー",
        "ハネモノ", "羽根", "甘デジ"
    ]

    s_keywords = [
        "ジャグラー", "マイジャグラー", "アイムジャグラー",
        "ゴーゴージャグラー", "ファンキージャグラー",
        "ハッピージャグラー", "沖ドキ", "ハナハナ",
        "チバリヨ", "バジリスク", "モンキーターン"
    ]

    for kw in p_keywords:
        if kw in name:
            return "P"

    for kw in s_keywords:
        if kw in name:
            return "S"

    return current_category


def minmax_score(series):
    s = pd.to_numeric(series, errors="coerce")
    if s.max() == s.min():
        return pd.Series([50] * len(s), index=s.index)
    return ((s - s.min()) / (s.max() - s.min()) * 100).round(2)


def grade(score):
    if score >= 85:
        return "S"
    if score >= 70:
        return "A"
    if score >= 55:
        return "B"
    if score >= 40:
        return "C"
    return "D"


def build_scores(df):
    df = df.copy()

    df["operation_score"] = minmax_score(df["avg_operation"])
    df["latest_operation_score"] = minmax_score(df["latest_operation"])
    df["profit_score_base"] = minmax_score(df["avg_gross_profit"])
    df["lifecycle_score_base"] = minmax_score(df["operation_contribution_weeks"])

    df["profit_tolerance_score"] = (
        df["profit_score_base"] * 0.55 +
        df["operation_score"] * 0.45
    ).round(2)

    df["popularity_score"] = (
        df["operation_score"] * 0.45 +
        df["latest_operation_score"] * 0.25 +
        df["lifecycle_score_base"] * 0.20 +
        df["profit_tolerance_score"] * 0.10
    ).round(2)

    df["profit_score"] = (
        df["profit_score_base"] * 0.60 +
        df["profit_tolerance_score"] * 0.25 +
        df["operation_score"] * 0.15
    ).round(2)

    df["lifecycle_score"] = (
        df["lifecycle_score_base"] * 0.60 +
        minmax_score(df["avg_operation_12w"]) * 0.25 +
        minmax_score(df["avg_operation_4w"]) * 0.15
    ).round(2)

    df["overall_score"] = (
        df["popularity_score"] * 0.45 +
        df["profit_score"] * 0.30 +
        df["lifecycle_score"] * 0.25
    ).round(2)

    df["overall_grade"] = df["overall_score"].apply(grade)

    return df


def main():
    perf = pd.read_csv(PERFORMANCE_CSV)
    master = pd.read_csv(MASTER_CSV)

    perf["category"] = perf.apply(
        lambda r: fix_category(r["machine_name"], r["category"]),
        axis=1
    )

    perf["report_date"] = pd.to_datetime(perf["report_date"], errors="coerce")
    perf["operation"] = pd.to_numeric(perf["operation"], errors="coerce")
    perf["sales"] = pd.to_numeric(perf["sales"], errors="coerce")
    perf["gross_profit"] = pd.to_numeric(perf["gross_profit"], errors="coerce")

    perf = perf.dropna(subset=["machine_name", "report_date"])
    perf = perf.sort_values(["machine_name", "report_date"])

    latest = (
        perf.groupby(["machine_name", "category"], as_index=False)
        .tail(1)[["machine_name", "category", "report_date", "operation", "sales", "gross_profit"]]
        .rename(columns={
            "report_date": "latest_report_date",
            "operation": "latest_operation",
            "sales": "latest_sales",
            "gross_profit": "latest_gross_profit"
        })
    )

    summary = (
        perf.groupby(["machine_name", "category"], as_index=False)
        .agg(
            first_report_date=("report_date", "min"),
            data_count=("operation", "count"),
            avg_operation=("operation", "mean"),
            max_operation=("operation", "max"),
            min_operation=("operation", "min"),
            avg_sales=("sales", "mean"),
            max_sales=("sales", "max"),
            avg_gross_profit=("gross_profit", "mean"),
            max_gross_profit=("gross_profit", "max"),
        )
    )

    contribution = (
        perf.assign(is_contribution_week=perf["operation"] >= 10000)
        .groupby(["machine_name", "category"], as_index=False)
        .agg(operation_contribution_weeks=("is_contribution_week", "sum"))
    )

    recent_4w = (
        perf.groupby(["machine_name", "category"])
        .apply(lambda g: g.sort_values("report_date").tail(4)["operation"].mean())
        .reset_index(name="avg_operation_4w")
    )

    recent_12w = (
        perf.groupby(["machine_name", "category"])
        .apply(lambda g: g.sort_values("report_date").tail(12)["operation"].mean())
        .reset_index(name="avg_operation_12w")
    )

    df = summary.merge(latest, on=["machine_name", "category"], how="left")
    df = df.merge(contribution, on=["machine_name", "category"], how="left")
    df = df.merge(recent_4w, on=["machine_name", "category"], how="left")
    df = df.merge(recent_12w, on=["machine_name", "category"], how="left")

    master_use = master[
        [
            "machine_name",
            "machine_id",
            "formal_machine_name",
            "maker_name",
            "series_name",
            "sub_series_name",
            "machine_type",
            "is_smart",
            "is_lt",
        ]
    ].copy()

    df = df.merge(master_use, on="machine_name", how="left")

    df = build_scores(df)

    df["ai_comment"] = df.apply(
        lambda r: (
            f"{r['machine_name']}は平均稼働{r['avg_operation']:.0f}、"
            f"平均粗利{r['avg_gross_profit']:.0f}、"
            f"稼働貢献週{int(r['operation_contribution_weeks'])}週。"
            f"人気指数{r['popularity_score']:.1f}、"
            f"粗利指数{r['profit_score']:.1f}、"
            f"寿命指数{r['lifecycle_score']:.1f}。"
        ),
        axis=1
    )

    df = df.sort_values(["category", "overall_score"], ascending=[True, False])

    df.to_csv(OUT_ALL, index=False, encoding="utf-8-sig")
    df[df["category"] == "P"].to_csv(OUT_P, index=False, encoding="utf-8-sig")
    df[df["category"] == "S"].to_csv(OUT_S, index=False, encoding="utf-8-sig")

    print("作成完了")
    print(f"全体: {OUT_ALL}")
    print(f"パチンコ: {OUT_P}")
    print(f"パチスロ: {OUT_S}")
    print()
    print("パチンコ上位20")
    print(
        df[df["category"] == "P"][
            ["machine_name", "overall_score", "overall_grade", "popularity_score", "profit_score", "lifecycle_score"]
        ].head(20).to_string(index=False)
    )
    print()
    print("パチスロ上位20")
    print(
        df[df["category"] == "S"][
            ["machine_name", "overall_score", "overall_grade", "popularity_score", "profit_score", "lifecycle_score"]
        ].head(20).to_string(index=False)
    )


if __name__ == "__main__":
    main()