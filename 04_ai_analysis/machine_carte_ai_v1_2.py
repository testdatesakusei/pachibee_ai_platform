# -*- coding: utf-8 -*-
"""
Machine Intelligence Engine v1.2
現役人気重視版

改善点：
- 現役人気ランキングと長期評価を分離
- 最新週に存在しない機種は現役ランキングから除外
- 直近4週・12週を強く評価
- 古い過去実績だけで上位に来る機種を減点
- P/Sランキングを必ず分離
"""

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]

PERFORMANCE_CSV = ROOT / "output" / "weekly_performance_import.csv"
MASTER_CSV = ROOT / "output" / "machine_master_v2.csv"

OUT_ALL = ROOT / "output" / "machine_carte_ai_v1_2_all.csv"
OUT_ACTIVE_P = ROOT / "output" / "machine_carte_ai_v1_2_active_P.csv"
OUT_ACTIVE_S = ROOT / "output" / "machine_carte_ai_v1_2_active_S.csv"
OUT_LEGEND_P = ROOT / "output" / "machine_carte_ai_v1_2_legend_P.csv"
OUT_LEGEND_S = ROOT / "output" / "machine_carte_ai_v1_2_legend_S.csv"


def fix_category(machine_name, current_category):
    name = str(machine_name).strip()

    # パチンコ強制判定
    if name.startswith(("P", "PA", "PF", "e", "CR", "CRA", "ぱちんこ", "パチンコ", "デジハネ")):
        return "P"

    # パチスロ強制判定
    if name.startswith(("L", "S", "スマスロ", "パチスロ", "SLOT")):
        return "S"

    p_keywords = [
        "北斗無双", "真・北斗無双", "海物語", "大海", "沖海",
        "牙狼", "フィーバー", "ハネモノ", "羽根", "甘デジ",
        "新世紀エヴァンゲリオン", "ウルトラ超光", "ぱちんこ",
        "P南国育ち", "遊moreLT", "エガブレイブ"
    ]

    s_keywords = [
        "ジャグラー", "マイジャグラー", "アイムジャグラー",
        "ゴーゴージャグラー", "ファンキージャグラー",
        "ハッピージャグラー", "沖ドキ", "ハナハナ",
        "チバリヨ", "バジリスク", "モンキーターン",
        "パチスロ聖闘士星矢", "BLACK LAGOON", "ギルティクラウン"
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
    s = s.replace([np.inf, -np.inf], np.nan)
    if s.notna().sum() == 0:
        return pd.Series([50] * len(s), index=s.index)
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

    perf = perf.dropna(subset=["machine_name", "report_date", "operation"])
    perf = perf.sort_values(["machine_name", "report_date"])

    latest_date = perf["report_date"].max()
    active_start_date = latest_date - pd.Timedelta(days=35)   # 直近5週以内に存在する機種を現役扱い
    recent12_start_date = latest_date - pd.Timedelta(days=84)

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

    recent4 = (
        perf[perf["report_date"] >= active_start_date]
        .groupby(["machine_name", "category"], as_index=False)
        .agg(
            avg_operation_4w=("operation", "mean"),
            avg_sales_4w=("sales", "mean"),
            avg_gross_profit_4w=("gross_profit", "mean"),
            recent_week_count=("operation", "count")
        )
    )

    recent12 = (
        perf[perf["report_date"] >= recent12_start_date]
        .groupby(["machine_name", "category"], as_index=False)
        .agg(
            avg_operation_12w=("operation", "mean"),
            avg_gross_profit_12w=("gross_profit", "mean"),
            recent12_week_count=("operation", "count")
        )
    )

    df = summary.merge(latest, on=["machine_name", "category"], how="left")
    df = df.merge(contribution, on=["machine_name", "category"], how="left")
    df = df.merge(recent4, on=["machine_name", "category"], how="left")
    df = df.merge(recent12, on=["machine_name", "category"], how="left")

    master_cols = [
        "machine_name", "machine_id", "formal_machine_name", "maker_name",
        "series_name", "sub_series_name", "machine_type", "is_smart", "is_lt"
    ]
    master_use = master[[c for c in master_cols if c in master.columns]].copy()
    df = df.merge(master_use, on="machine_name", how="left")

    df["is_active"] = df["latest_report_date"] >= active_start_date

    # 現役ランキング用スコア
    df["latest_operation_score"] = minmax_score(df["latest_operation"])
    df["recent4_operation_score"] = minmax_score(df["avg_operation_4w"])
    df["recent12_operation_score"] = minmax_score(df["avg_operation_12w"])
    df["recent_profit_score"] = minmax_score(df["avg_gross_profit_4w"])
    df["long_lifecycle_score"] = minmax_score(df["operation_contribution_weeks"])

    # 最新週ランキング順位。直近圏外の判定に使う
    df["latest_rank_in_category"] = (
        df.groupby("category")["latest_operation"]
        .rank(method="min", ascending=False)
    )

    # 直近50位圏外は現役人気では減点
    df["recent_rank_penalty"] = np.where(df["latest_rank_in_category"] > 50, 20, 0)

    # 現役人気指数：直近重視
    df["active_popularity_score"] = (
        df["recent4_operation_score"] * 0.40 +
        df["latest_operation_score"] * 0.30 +
        df["recent12_operation_score"] * 0.15 +
        df["recent_profit_score"] * 0.10 +
        df["long_lifecycle_score"] * 0.05 -
        df["recent_rank_penalty"]
    ).round(2)

    df["active_popularity_score"] = df["active_popularity_score"].clip(lower=0, upper=100)

    # 長期名機指数：過去実績も評価
    df["legend_score"] = (
        minmax_score(df["avg_operation"]) * 0.30 +
        minmax_score(df["max_operation"]) * 0.20 +
        df["long_lifecycle_score"] * 0.30 +
        minmax_score(df["avg_gross_profit"]) * 0.20
    ).round(2)

    # ホール資産指数：粗利と現役性
    df["asset_score"] = (
        minmax_score(df["avg_gross_profit"]) * 0.35 +
        minmax_score(df["avg_gross_profit_4w"]) * 0.25 +
        df["recent4_operation_score"] * 0.25 +
        df["long_lifecycle_score"] * 0.15
    ).round(2)

    df["active_grade"] = df["active_popularity_score"].apply(grade)
    df["legend_grade"] = df["legend_score"].apply(grade)
    df["asset_grade"] = df["asset_score"].apply(grade)

    df["ai_comment"] = df.apply(
        lambda r: (
            f"{r['machine_name']}は最新稼働{r['latest_operation']:.0f}、"
            f"直近4週平均稼働{0 if pd.isna(r['avg_operation_4w']) else r['avg_operation_4w']:.0f}、"
            f"稼働貢献週{int(0 if pd.isna(r['operation_contribution_weeks']) else r['operation_contribution_weeks'])}週。"
            f"現役人気指数{r['active_popularity_score']:.1f}、"
            f"長期名機指数{r['legend_score']:.1f}、"
            f"ホール資産指数{r['asset_score']:.1f}。"
        ),
        axis=1
    )

    df = df.sort_values(["category", "active_popularity_score"], ascending=[True, False])

    active_df = df[df["is_active"] == True].copy()

    active_p = active_df[active_df["category"] == "P"].sort_values("active_popularity_score", ascending=False)
    active_s = active_df[active_df["category"] == "S"].sort_values("active_popularity_score", ascending=False)

    legend_p = df[df["category"] == "P"].sort_values("legend_score", ascending=False)
    legend_s = df[df["category"] == "S"].sort_values("legend_score", ascending=False)

    df.to_csv(OUT_ALL, index=False, encoding="utf-8-sig")
    active_p.to_csv(OUT_ACTIVE_P, index=False, encoding="utf-8-sig")
    active_s.to_csv(OUT_ACTIVE_S, index=False, encoding="utf-8-sig")
    legend_p.to_csv(OUT_LEGEND_P, index=False, encoding="utf-8-sig")
    legend_s.to_csv(OUT_LEGEND_S, index=False, encoding="utf-8-sig")

    print("作成完了")
    print(f"最新日: {latest_date.date()}")
    print(f"現役判定開始日: {active_start_date.date()}")
    print()
    print("現役パチンコ上位20")
    print(
        active_p[
            ["machine_name", "latest_operation", "avg_operation_4w", "active_popularity_score", "active_grade", "legend_score", "asset_score"]
        ].head(20).to_string(index=False)
    )
    print()
    print("現役パチスロ上位20")
    print(
        active_s[
            ["machine_name", "latest_operation", "avg_operation_4w", "active_popularity_score", "active_grade", "legend_score", "asset_score"]
        ].head(20).to_string(index=False)
    )
    print()
    print("長期名機 パチンコ上位10")
    print(
        legend_p[
            ["machine_name", "legend_score", "active_popularity_score", "latest_operation", "avg_operation_4w"]
        ].head(10).to_string(index=False)
    )
    print()
    print("長期名機 パチスロ上位10")
    print(
        legend_s[
            ["machine_name", "legend_score", "active_popularity_score", "latest_operation", "avg_operation_4w"]
        ].head(10).to_string(index=False)
    )


if __name__ == "__main__":
    main()