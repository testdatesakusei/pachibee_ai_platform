# -*- coding: utf-8 -*-
"""
機種マスター候補作成 v1
output/base_excel_import_preview.csv から機種一覧を作る。
まだSupabaseには登録しない安全版。
"""

from pathlib import Path
import pandas as pd
import re

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "output" / "base_excel_import_preview.csv"
OUT = ROOT / "output" / "machine_master_candidates.csv"


def judge_category(machine_name: str, current_category: str) -> str:
    name = str(machine_name)

    # パチンコ判定
    p_keywords = [
        "ぱちんこ", "パチンコ", "P ", "P-", "P_", "PA", "PF", "CR", "CRA",
        "e ", "eF", "eフィーバー", "デジハネ", "甘デジ", "羽根", "ハネモノ",
        "海物語", "大海", "沖海", "牙狼", "エヴァ", "北斗無双",
        "真・花の慶次", "ルパン", "リゼロ鬼がかり"
    ]

    # パチスロ判定
    s_keywords = [
        "L ", "L-", "スマスロ", "パチスロ", "スロット", "S ",
        "マイジャグラー", "アイムジャグラー", "ゴーゴージャグラー",
        "ファンキージャグラー", "ハッピージャグラー", "ジャグラー",
        "沖ドキ", "ハナハナ", "チバリヨ", "番長", "吉宗",
        "バジリスク", "北斗の拳", "モンキーターン", "ヴァルヴレイヴ"
    ]

    for kw in p_keywords:
        if name.startswith(kw) or kw in name:
            return "P"

    for kw in s_keywords:
        if name.startswith(kw) or kw in name:
            return "S"

    if current_category in ["P", "S"]:
        return current_category

    return "UNKNOWN"


def normalize_machine_name(name: str) -> str:
    s = str(name).strip()
    s = re.sub(r"\s+", " ", s)
    s = s.replace("　", " ")
    return s


def main():
    if not SRC.exists():
        print("output/base_excel_import_preview.csv がありません。先に import_base_excel.py を実行してください。")
        return

    df = pd.read_csv(SRC)

    df["machine_name"] = df["machine_name"].astype(str).map(normalize_machine_name)
    df["category_fixed"] = df.apply(
        lambda r: judge_category(r["machine_name"], r.get("category", "")),
        axis=1
    )

    grouped = (
        df.groupby("machine_name", as_index=False)
        .agg(
            category=("category_fixed", lambda x: x.value_counts().index[0]),
            maker_name=("maker_name", lambda x: x.dropna().astype(str).value_counts().index[0] if len(x.dropna()) else ""),
            first_report_date=("report_date", "min"),
            latest_report_date=("report_date", "max"),
            data_count=("machine_name", "count"),
            avg_operation=("operation", "mean"),
            avg_sales=("sales", "mean"),
            avg_gross_profit=("gross_profit", "mean"),
        )
    )

    grouped = grouped.sort_values(["category", "latest_report_date", "data_count"], ascending=[True, False, False])

    grouped.to_csv(OUT, index=False, encoding="utf-8-sig")

    print(f"作成完了: {OUT}")
    print(f"機種数: {len(grouped)}")
    print(grouped["category"].value_counts(dropna=False))


if __name__ == "__main__":
    main()