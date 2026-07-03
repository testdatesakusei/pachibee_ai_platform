# -*- coding: utf-8 -*-
"""
機種マスター作成 v2
目的：
- 安易に「北斗」「海」「エヴァ」などで同一機種扱いしない
- 正式機種名は基本そのまま保持
- シリーズ名だけ別列で抽出
- P/S、メーカー、初出日、最新日、平均稼働、平均粗利を整理
"""

from pathlib import Path
import re
import pandas as pd
import hashlib

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "output" / "machine_master_candidates.csv"
OUT = ROOT / "output" / "machine_master_v2.csv"


def make_machine_id(category: str, machine_name: str) -> str:
    base = f"{category}_{machine_name}"
    h = hashlib.md5(base.encode("utf-8")).hexdigest()[:10]
    return f"{category}_{h}"


def normalize_text(s: str) -> str:
    s = str(s).strip()
    s = s.replace("　", " ")
    s = re.sub(r"\s+", " ", s)
    return s


def detect_series(machine_name: str) -> str:
    name = str(machine_name)

    rules = [
        ("北斗の拳", ["北斗の拳", "北斗無双", "北斗"]),
        ("海物語", ["海物語", "大海", "沖海", "スーパー海", "PA海"]),
        ("エヴァンゲリオン", ["エヴァ", "新世紀エヴァンゲリオン"]),
        ("牙狼", ["牙狼", "GARO"]),
        ("花の慶次", ["花の慶次", "真・花の慶次", "慶次"]),
        ("ジャグラー", ["ジャグラー", "マイジャグラー", "アイムジャグラー", "ゴーゴージャグラー", "ファンキージャグラー", "ハッピージャグラー"]),
        ("沖ドキ", ["沖ドキ"]),
        ("ハナハナ", ["ハナハナ"]),
        ("バジリスク", ["バジリスク", "絆", "天膳"]),
        ("モンキーターン", ["モンキーターン"]),
        ("番長", ["番長", "押忍!番長"]),
        ("吉宗", ["吉宗"]),
        ("東京喰種", ["東京喰種"]),
        ("ソードアート・オンライン", ["ソードアート・オンライン", "SAO"]),
        ("リゼロ", ["Re:ゼロ", "リゼロ"]),
        ("ルパン三世", ["ルパン"]),
        ("まどか☆マギカ", ["まどか", "魔法少女まどか"]),
        ("戦国乙女", ["戦国乙女"]),
        ("ゴッド", ["ミリオンゴッド", "ゴッド", "GOD"]),
    ]

    for series, keywords in rules:
        for kw in keywords:
            if kw in name:
                return series

    return ""


def detect_sub_series(machine_name: str) -> str:
    name = str(machine_name)

    sub_rules = [
        ("転生", ["転生"]),
        ("無双", ["無双"]),
        ("暴凶星", ["暴凶星"]),
        ("慈母", ["慈母"]),
        ("宿命", ["宿命"]),
        ("修羅", ["修羅"]),
        ("大海5", ["大海物語5", "大海5"]),
        ("沖海5", ["沖海5"]),
        ("沖海6", ["沖海6"]),
        ("海門決戦", ["海門決戦"]),
        ("天膳", ["天膳"]),
        ("絆", ["絆"]),
        ("GGO", ["GGO"]),
        ("鬼がかり", ["鬼がかり"]),
        ("Season2", ["season2", "Season2"]),
    ]

    for sub, keywords in sub_rules:
        for kw in keywords:
            if kw in name:
                return sub

    return ""


def detect_machine_type(machine_name: str, category: str) -> str:
    name = str(machine_name)

    if category == "S":
        if name.startswith("L") or "スマスロ" in name:
            return "スマスロ"
        if "ジャグラー" in name or "ハナハナ" in name:
            return "Aタイプ/ノーマル"
        if "沖ドキ" in name or "チバリヨ" in name:
            return "沖スロ"
        if "パチスロ" in name or name.startswith("S"):
            return "パチスロ"
        return "スロット"

    if category == "P":
        if name.startswith("e") or "スマパチ" in name:
            return "スマパチ"
        if "甘" in name or "99" in name or "PA" in name or "デジハネ" in name:
            return "甘デジ/ライト"
        if "LT" in name or "ラッキートリガー" in name:
            return "LT"
        if "羽根" in name or "ハネモノ" in name:
            return "羽根物"
        return "パチンコ"

    return ""


def main():
    if not SRC.exists():
        print("machine_master_candidates.csv がありません。先に create_machine_master.py を実行してください。")
        return

    df = pd.read_csv(SRC)

    df["machine_name"] = df["machine_name"].map(normalize_text)
    df["formal_machine_name"] = df["machine_name"]

    df["series_name"] = df["formal_machine_name"].map(detect_series)
    df["sub_series_name"] = df["formal_machine_name"].map(detect_sub_series)
    df["machine_type"] = df.apply(lambda r: detect_machine_type(r["formal_machine_name"], r["category"]), axis=1)

    df["is_smart"] = df["machine_type"].isin(["スマスロ", "スマパチ"])
    df["is_lt"] = df["formal_machine_name"].astype(str).str.contains("LT|ラッキートリガー", regex=True)
    df["machine_id"] = df.apply(lambda r: make_machine_id(r["category"], r["formal_machine_name"]), axis=1)

    df["merge_policy"] = "原則統合しない"
    df["merge_note"] = "同一シリーズでも別仕様・別導入日は別機種として扱う"

    cols = [
        "machine_id",
        "formal_machine_name",
        "machine_name",
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
        "avg_sales",
        "avg_gross_profit",
        "merge_policy",
        "merge_note",
    ]

    df = df[cols].sort_values(
        ["category", "series_name", "formal_machine_name"]
    )

    df.to_csv(OUT, index=False, encoding="utf-8-sig")

    print(f"作成完了: {OUT}")
    print(f"機種数: {len(df)}")
    print("カテゴリ別")
    print(df["category"].value_counts())
    print("シリーズ上位")
    print(df["series_name"].value_counts().head(20))


if __name__ == "__main__":
    main()