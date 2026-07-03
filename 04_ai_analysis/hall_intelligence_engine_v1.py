# -*- coding: utf-8 -*-
"""
Hall Intelligence Engine v1

output/hall_data_template.csv を読み込み、
ホールAIスコアを計算して
output/hall_intelligence_v1.csv を出力する。
"""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"

INPUT_CSV = OUTPUT / "hall_data_template.csv"
OUT_CSV = OUTPUT / "hall_intelligence_v1.csv"


def judge_grade(score):
    if score >= 95:
        return "S"
    if score >= 85:
        return "A"
    if score >= 70:
        return "B"
    if score >= 60:
        return "C"
    return "D"


def judge_type(row):
    if row["juggler_score"] >= 85:
        return "ジャグラー強化型"
    if row["smart_slot_score"] >= 85:
        return "スマスロ強化型"
    if row["pachinko_score"] >= 85:
        return "パチンコ強化型"
    return "バランス型"


def create_ai_comment(row):
    return (
        f"{row['hall_name']}はAI営業評価{row['ai_score']}点。"
        f"営業タイプは{row['hall_type']}。"
        f"稼働{row['avg_operation_score']}点、"
        f"利益{row['avg_profit_score']}点、"
        f"還元{row['return_score']}点、"
        f"ジャグラー{row['juggler_score']}点、"
        f"スマスロ{row['smart_slot_score']}点、"
        f"パチンコ{row['pachinko_score']}点。"
        f"強いカテゴリを維持しつつ、弱いカテゴリの改善が次の課題。"
    )


def main():
    if not INPUT_CSV.exists():
        print("入力CSVがありません。")
        print(f"先に作成してください: {INPUT_CSV}")
        return

    df = pd.read_csv(INPUT_CSV)

    required_cols = [
        "hall_name",
        "area",
        "avg_operation_score",
        "avg_profit_score",
        "return_score",
        "juggler_score",
        "smart_slot_score",
        "pachinko_score",
        "event_score",
        "new_machine_score",
        "market_score",
        "future_score",
    ]

    missing = [c for c in required_cols if c not in df.columns]

    if missing:
        print("必要な列が不足しています。")
        print(missing)
        return

    score_cols = [
        "avg_operation_score",
        "avg_profit_score",
        "return_score",
        "juggler_score",
        "smart_slot_score",
        "pachinko_score",
        "event_score",
        "new_machine_score",
        "market_score",
        "future_score",
    ]

    for col in score_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["ai_score"] = (
        df["avg_operation_score"] * 0.20
        + df["avg_profit_score"] * 0.20
        + df["return_score"] * 0.10
        + df["juggler_score"] * 0.10
        + df["smart_slot_score"] * 0.10
        + df["pachinko_score"] * 0.10
        + df["event_score"] * 0.05
        + df["new_machine_score"] * 0.05
        + df["market_score"] * 0.05
        + df["future_score"] * 0.05
    ).round(2)

    df["grade"] = df["ai_score"].apply(judge_grade)
    df["hall_type"] = df.apply(judge_type, axis=1)
    df["ai_comment"] = df.apply(create_ai_comment, axis=1)

    df = df.sort_values("ai_score", ascending=False)

    df.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")

    print("作成完了")
    print(f"入力: {INPUT_CSV}")
    print(f"出力: {OUT_CSV}")
    print(f"件数: {len(df)}")
    print()
    print(
        df[
            [
                "hall_name",
                "area",
                "ai_score",
                "grade",
                "hall_type",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()