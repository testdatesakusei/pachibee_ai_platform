# -*- coding: utf-8 -*-
"""
Machine Intelligence Engine v1
機種カルテAI 初期版

目的：
- 週次実績34,133件から機種別カルテを作る
- 平均稼働、最新稼働、平均粗利、稼働貢献週などを計算
- 人気指数、粗利指数、寿命指数を仮計算
- まだSupabaseには登録しない安全版
"""

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]

PERFORMANCE_CSV = ROOT / "output" / "weekly_performance_import.csv"
MASTER_CSV = ROOT / "output" / "machine_master_v2.csv"
OUT = ROOT / "output" / "machine_carte_ai_v1.csv"


def minmax_score(series):
    s = pd.to_numeric(series, errors="coerce")
    if s.max() == s.min():
        return pd.Series([50] * len(s), index=s.index)
    return ((s - s.min()) / (s.max() - s.min()) * 100).round(2)


def main():
    if not PERFORMANCE_CSV.exists():
        print("weekly_performance_import.csv がありません。")
        return

    if not MASTER_CSV.exists():
        print("machine_master_v2.csv がありません。")
        return

    perf = pd.read_csv(PERFORMANCE_CSV)
    master = pd.read_csv(MASTER_CSV)

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

    # 稼働貢献週：仮に稼働10,000以上を貢献週として数える
    contribution = (
        perf.assign(is_contribution_week=perf["operation"] >= 10000)
        .groupby(["machine_name", "category"], as_index=False)
        .agg(operation_contribution_weeks=("is_contribution_week", "sum"))
    )

    # 直近4週・12週平均
    def recent_avg(g, n):
        return g.sort_values("report_date").tail(n)["operation"].mean()

    recent_4w = (
        perf.groupby(["machine_name", "category"])
        .apply(lambda g: recent_avg(g, 4))
        .reset_index(name="avg_operation_4w")
    )

    recent_12w = (
        perf.groupby(["machine_name", "category"])
        .apply(lambda g: recent_avg(g, 12))
        .reset_index(name="avg_operation_12w")
    )

    df = summary.merge(latest, on=["machine_name", "category"], how="left")
    df = df.merge(contribution, on=["machine_name", "category"], how="left")
    df = df.merge(recent_4w, on=["machine_name", "category"], how="left")
    df = df.merge(recent_12w, on=["machine_name", "category"], how="left")

    # マスター情報を付与
    master_cols = [
        "formal_machine_name",
        "machine_name",
        "machine_id",
        "maker_name",
        "series_name",
        "sub_series_name",
        "machine_type",
        "is_smart",
        "is_lt",
    ]

    master_use = master[[c for c in master_cols if c in master.columns]].copy()

    df = df.merge(
        master_use,
        on="machine_name",
        how="left"
    )

    # スコア計算用
    df["operation_score"] = minmax_score(df["avg_operation"])
    df["latest_operation_score"] = minmax_score(df["latest_operation"])
    df["profit_score_base"] = minmax_score(df["avg_gross_profit"])
    df["lifecycle_score_base"] = minmax_score(df["operation_contribution_weeks"])

    # 粗利耐性：粗利が高く、稼働も平均以上なら高評価
    df["profit_tolerance_score"] = (
        df["profit_score_base"] * 0.55 +
        df["operation_score"] * 0.45
    ).round(2)

    # 人気指数 v1
    df["popularity_score"] = (
        df["operation_score"] * 0.45 +
        df["latest_operation_score"] * 0.25 +
        df["lifecycle_score_base"] * 0.20 +
        df["profit_tolerance_score"] * 0.10
    ).round(2)

    # 粗利指数 v1
    df["profit_score"] = (
        df["profit_score_base"] * 0.60 +
        df["profit_tolerance_score"] * 0.25 +
        df["operation_score"] * 0.15
    ).round(2)

    # 寿命指数 v1
    df["lifecycle_score"] = (
        df["lifecycle_score_base"] * 0.60 +
        df["avg_operation_12w"].pipe(minmax_score) * 0.25 +
        df["avg_operation_4w"].pipe(minmax_score) * 0.15
    ).round(2)

    # 総合ランク
    df["overall_score"] = (
        df["popularity_score"] * 0.45 +
        df["profit_score"] * 0.30 +
        df["lifecycle_score"] * 0.25
    ).round(2)

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

    df["overall_grade"] = df["overall_score"].apply(grade)

    # 簡易AIコメント
    def comment(r):
        return (
            f"{r['machine_name']}は、平均稼働{r['avg_operation']:.0f}、"
            f"平均粗利{r['avg_gross_profit']:.0f}、稼働貢献週{int(r['operation_contribution_weeks'])}週。"
            f"人気指数{r['popularity_score']:.1f}、粗利指数{r['profit_score']:.1f}、"
            f"寿命指数{r['lifecycle_score']:.1f}の評価。"
        )

    df["ai_comment"] = df.apply(comment, axis=1)

    cols = [
        "machine_id",
        "machine_name",
        "formal_machine_name",
        "category",
        "maker_name",
        "series_name",
        "sub_series_name",
        "machine_type",
        "is_smart",
        "is_lt",
        "first_report_date",
        "latest_report_date",
        "data_count",
        "avg_operation",
        "latest_operation",
        "avg_operation_4w",
        "avg_operation_12w",
        "max_operation",
        "min_operation",
        "avg_sales",
        "latest_sales",
        "avg_gross_profit",
        "latest_gross_profit",
        "operation_contribution_weeks",
        "popularity_score",
        "profit_score",
        "lifecycle_score",
        "profit_tolerance_score",
        "overall_score",
        "overall_grade",
        "ai_comment",
    ]

    df = df[[c for c in cols if c in df.columns]]
    df = df.sort_values("overall_score", ascending=False)

    df.to_csv(OUT, index=False, encoding="utf-8-sig")

    print("作成完了")
    print(f"出力: {OUT}")
    print(f"機種数: {len(df)}")
    print("上位20機種")
    print(df[["machine_name", "category", "overall_score", "overall_grade", "popularity_score", "profit_score", "lifecycle_score"]].head(20).to_string(index=False))


if __name__ == "__main__":
    main()