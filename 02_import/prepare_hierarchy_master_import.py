# -*- coding: utf-8 -*-
"""
6階層マスター登録用CSV作成 v1
machine_master_v2.csv から以下を作る。

- maker_master_import.csv
- brand_master_import.csv
- series_hierarchy_master_import.csv
- machine_hierarchy_master_import.csv

まだSupabaseには登録しない安全版。
"""

from pathlib import Path
import pandas as pd
import hashlib

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "output" / "machine_master_v2.csv"
OUT_DIR = ROOT / "output"


def make_hash_id(prefix: str, value: str) -> str:
    h = hashlib.md5(str(value).encode("utf-8")).hexdigest()[:10]
    return f"{prefix}_{h}"


def clean_text(x):
    if pd.isna(x):
        return ""
    return str(x).strip()


def main():
    if not SRC.exists():
        print("machine_master_v2.csv がありません。先に build_machine_master_v2.py を実行してください。")
        return

    df = pd.read_csv(SRC)
    df = df.fillna("")

    df["maker_name"] = df["maker_name"].map(clean_text)
    df["series_name"] = df["series_name"].map(clean_text)
    df["formal_machine_name"] = df["formal_machine_name"].map(clean_text)

    maker = (
        df[df["maker_name"] != ""][["maker_name"]]
        .drop_duplicates()
        .sort_values("maker_name")
        .copy()
    )
    maker["maker_group"] = ""
    maker["memo"] = "ベースExcelから自動生成"

    brand = (
        df[["maker_name", "series_name", "category"]]
        .copy()
    )
    brand["brand_name"] = brand["series_name"]
    brand.loc[brand["brand_name"] == "", "brand_name"] = "未分類"
    brand = brand[["brand_name", "maker_name", "category"]].drop_duplicates()
    brand["category_hint"] = brand["category"]
    brand["memo"] = "series_nameを初期ブランドとして登録"

    series = (
        df[["series_name", "maker_name", "category"]]
        .copy()
    )
    series.loc[series["series_name"] == "", "series_name"] = "未分類"
    series["brand_name"] = series["series_name"]
    series["category_hint"] = series["category"]
    series["parent_series_name"] = ""
    series["memo"] = "ベースExcelから自動生成"
    series = series[["series_name", "brand_name", "maker_name", "parent_series_name", "category_hint", "memo"]].drop_duplicates()

    machine = df[[
        "machine_id",
        "formal_machine_name",
        "category",
        "maker_name",
        "series_name",
        "machine_type",
        "first_report_date",
        "latest_report_date",
    ]].copy()

    machine.loc[machine["series_name"] == "", "series_name"] = "未分類"
    machine["brand_name"] = machine["series_name"]
    machine["is_active"] = True
    machine["memo"] = "ベースExcelから自動生成"

    maker.to_csv(OUT_DIR / "maker_master_import.csv", index=False, encoding="utf-8-sig")
    brand.to_csv(OUT_DIR / "brand_master_import.csv", index=False, encoding="utf-8-sig")
    series.to_csv(OUT_DIR / "series_hierarchy_master_import.csv", index=False, encoding="utf-8-sig")
    machine.to_csv(OUT_DIR / "machine_hierarchy_master_import.csv", index=False, encoding="utf-8-sig")

    print("作成完了")
    print(f"メーカー: {len(maker)}件")
    print(f"ブランド: {len(brand)}件")
    print(f"シリーズ: {len(series)}件")
    print(f"機種: {len(machine)}件")


if __name__ == "__main__":
    main()