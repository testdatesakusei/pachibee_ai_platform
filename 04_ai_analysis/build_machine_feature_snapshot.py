# -*- coding: utf-8 -*-
"""
Feature Snapshot 作成 v1
週次実績データから、機種ごとのAI用特徴量を作成する安全版。
まだSupabaseには登録せず、CSV出力だけ行う。
"""

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]

PERF_CSV = ROOT / "output" / "weekly_performance_import.csv"
MASTER_CSV = ROOT / "output" / "machine_master_v2.csv"
OUT_CSV = ROOT / "output" / "machine_feature_snapshot_v1.csv"


def score_minmax(s):
    s = pd.to_numeric(s, errors="coerce")
    if s.notna().sum() == 0 or s.max() == s.min():
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


def main():
    perf = pd.read_csv(PERF_CSV)
    master = pd.read_csv(MASTER_CSV)

    perf["report_date"] = pd.to_datetime(perf["report_date"], errors="coerce")
    perf["operation"] = pd.to_numeric(perf["operation"], errors="coerce")
    perf["sales"] = pd.to_numeric(perf["sales"], errors="coerce")
    perf["gross_profit"] = pd.to_numeric(perf["gross_profit"], errors="coerce")

    latest_date = perf["report_date"].max()
    start_4w = latest_date - pd.Timedelta(days=35)
    start_12w = latest_date - pd.Timedelta(days=84)

    latest = (
        perf.sort_values("report_date")
        .groupby(["machine_name", "category"], as_index=False)
        .tail(1)
        .rename(columns={
            "operation": "latest_operation",
            "sales": "latest_sales",
            "gross_profit": "latest_gross_profit",
        })
    )

    all_summary = (
        perf.groupby(["machine_name", "category"], as_index=False)
        .agg(
            avg_operation_all=("operation", "mean"),
            max_operation=("operation", "max"),
            min_operation=("operation", "min"),
            avg_sales_all=("sales", "mean"),
            avg_gross_profit_all=("gross_profit", "mean"),
        )
    )

    summary_4w = (
        perf[perf["report_date"] >= start_4w]
        .groupby(["machine_name", "category"], as_index=False)
        .agg(
            avg_operation_4w=("operation", "mean"),
            avg_sales_4w=("sales", "mean"),
            avg_gross_profit_4w=("gross_profit", "mean"),
        )
    )

    summary_12w = (
        perf[perf["report_date"] >= start_12w]
        .groupby(["machine_name", "category"], as_index=False)
        .agg(
            avg_operation_12w=("operation", "mean"),
            avg_sales_12w=("sales", "mean"),
            avg_gross_profit_12w=("gross_profit", "mean"),
        )
    )

    contribution = (
        perf.assign(is_contribution_week=perf["operation"] >= 10000)
        .groupby(["machine_name", "category"], as_index=False)
        .agg(operation_contribution_weeks=("is_contribution_week", "sum"))
    )

    df = latest[[
        "machine_name", "category", "report_date",
        "latest_operation", "latest_sales", "latest_gross_profit"
    ]].rename(columns={"report_date": "latest_report_date"})

    df = df.merge(all_summary, on=["machine_name", "category"], how="left")
    df = df.merge(summary_4w, on=["machine_name", "category"], how="left")
    df = df.merge(summary_12w, on=["machine_name", "category"], how="left")
    df = df.merge(contribution, on=["machine_name", "category"], how="left")

    master_cols = [
        "machine_id", "machine_name", "formal_machine_name", "maker_name",
        "series_name", "machine_type", "is_smart", "is_lt"
    ]
    master_use = master[[c for c in master_cols if c in master.columns]]
    df = df.merge(master_use, on="machine_name", how="left")

    df["report_date"] = latest_date.date()

    df["operation_score"] = score_minmax(df["avg_operation_4w"])
    df["latest_operation_score"] = score_minmax(df["latest_operation"])
    df["profit_base_score"] = score_minmax(df["avg_gross_profit_4w"])
    df["lifecycle_base_score"] = score_minmax(df["operation_contribution_weeks"])

    df["profit_tolerance_score"] = (
        df["profit_base_score"] * 0.55 +
        df["operation_score"] * 0.45
    ).round(2)

    df["popularity_score"] = (
        df["operation_score"] * 0.45 +
        df["latest_operation_score"] * 0.35 +
        df["lifecycle_base_score"] * 0.10 +
        df["profit_tolerance_score"] * 0.10
    ).round(2)

    df["profit_score"] = (
        df["profit_base_score"] * 0.60 +
        df["profit_tolerance_score"] * 0.25 +
        df["operation_score"] * 0.15
    ).round(2)

    df["lifecycle_score"] = (
        df["lifecycle_base_score"] * 0.50 +
        score_minmax(df["avg_operation_12w"]) * 0.30 +
        score_minmax(df["avg_operation_4w"]) * 0.20
    ).round(2)

    df["market_score"] = 0
    df["asset_score"] = (
        df["profit_score"] * 0.45 +
        df["popularity_score"] * 0.35 +
        df["lifecycle_score"] * 0.20
    ).round(2)

    df["recommendation_score"] = (
        df["popularity_score"] * 0.50 +
        df["asset_score"] * 0.30 +
        df["lifecycle_score"] * 0.20
    ).round(2)

    df["overall_score"] = (
        df["popularity_score"] * 0.45 +
        df["profit_score"] * 0.25 +
        df["lifecycle_score"] * 0.20 +
        df["asset_score"] * 0.10
    ).round(2)

    df["overall_grade"] = df["overall_score"].apply(grade)

    df["score_reason"] = df.apply(
        lambda r: (
            f"直近4週稼働={r['avg_operation_4w']:.0f}, "
            f"最新稼働={r['latest_operation']:.0f}, "
            f"平均粗利4週={r['avg_gross_profit_4w']:.0f}, "
            f"稼働貢献週={r['operation_contribution_weeks']:.0f}"
        ),
        axis=1
    )

    df["ai_comment"] = df.apply(
        lambda r: (
            f"{r['machine_name']}は直近4週平均稼働{r['avg_operation_4w']:.0f}、"
            f"最新稼働{r['latest_operation']:.0f}。"
            f"人気指数{r['popularity_score']:.1f}、"
            f"粗利指数{r['profit_score']:.1f}、"
            f"寿命指数{r['lifecycle_score']:.1f}。"
        ),
        axis=1
    )

    output_cols = [
        "machine_id", "machine_name", "category", "report_date",
        "maker_name", "series_name", "machine_type", "is_smart", "is_lt",
        "latest_operation", "avg_operation_4w", "avg_operation_12w",
        "avg_operation_all", "max_operation", "min_operation",
        "operation_contribution_weeks",
        "latest_sales", "avg_sales_4w", "avg_sales_12w", "avg_sales_all",
        "latest_gross_profit", "avg_gross_profit_4w",
        "avg_gross_profit_12w", "avg_gross_profit_all",
        "profit_tolerance_score",
        "popularity_score", "profit_score", "lifecycle_score",
        "market_score", "asset_score", "recommendation_score",
        "overall_score", "overall_grade",
        "score_reason", "ai_comment",
    ]

    df = df[[c for c in output_cols if c in df.columns]]
    df = df.sort_values(["category", "overall_score"], ascending=[True, False])

    df.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")

    print("作成完了")
    print(f"出力: {OUT_CSV}")
    print(f"件数: {len(df)}")
    print()
    print("パチンコ上位10")
    print(df[df["category"] == "P"][["machine_name", "overall_score", "popularity_score", "profit_score", "lifecycle_score"]].head(10).to_string(index=False))
    print()
    print("パチスロ上位10")
    print(df[df["category"] == "S"][["machine_name", "overall_score", "popularity_score", "profit_score", "lifecycle_score"]].head(10).to_string(index=False))


if __name__ == "__main__":
    main()