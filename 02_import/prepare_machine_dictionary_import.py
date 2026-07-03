# -*- coding: utf-8 -*-
"""
機種辞書DB登録用CSV作成 v1
machine_master_v2.csv から Supabase登録用CSVを作る
"""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "output" / "machine_master_v2.csv"

OUT_DICT = ROOT / "output" / "machine_dictionary_import.csv"
OUT_ALIAS = ROOT / "output" / "machine_alias_import.csv"
OUT_REVIEW = ROOT / "output" / "machine_classification_review.csv"


def main():
    if not SRC.exists():
        print("machine_master_v2.csv がありません。先に build_machine_master_v2.py を実行してください。")
        return

    df = pd.read_csv(SRC)

    dictionary = pd.DataFrame({
        "machine_id": df["machine_id"],
        "formal_machine_name": df["formal_machine_name"],
        "category": df["category"],
        "maker_name": df["maker_name"],
        "series_name": df["series_name"],
        "sub_series_name": df["sub_series_name"],
        "spec_name": "",
        "machine_type": df["machine_type"],
        "is_smart": df["is_smart"],
        "is_lt": df["is_lt"],
        "is_bt": False,
        "release_date": "",
        "first_report_date": df["first_report_date"],
        "latest_report_date": df["latest_report_date"],
        "data_count": df["data_count"],
        "avg_operation": df["avg_operation"],
        "avg_sales": df["avg_sales"],
        "avg_gross_profit": df["avg_gross_profit"],
        "classification_status": "auto_v1",
        "review_required": df["series_name"].isna() | (df["series_name"].astype(str).str.strip() == ""),
        "memo": "ベースExcel340ファイルから自動生成"
    })

    alias = pd.DataFrame({
        "alias_name": df["machine_name"],
        "machine_id": df["machine_id"],
        "formal_machine_name": df["formal_machine_name"],
        "confidence_score": 1.0,
        "memo": "初期自動登録"
    })

    review = dictionary[dictionary["review_required"] == True].copy()
    review_out = pd.DataFrame({
        "raw_machine_name": review["formal_machine_name"],
        "suggested_machine_id": review["machine_id"],
        "suggested_formal_machine_name": review["formal_machine_name"],
        "suggested_category": review["category"],
        "suggested_series_name": review["series_name"],
        "suggested_sub_series_name": review["sub_series_name"],
        "suggested_machine_type": review["machine_type"],
        "reason": "series_name未分類のため確認推奨",
        "review_status": "pending"
    })

    dictionary.to_csv(OUT_DICT, index=False, encoding="utf-8-sig")
    alias.to_csv(OUT_ALIAS, index=False, encoding="utf-8-sig")
    review_out.to_csv(OUT_REVIEW, index=False, encoding="utf-8-sig")

    print("作成完了")
    print(f"機種辞書: {OUT_DICT} / {len(dictionary)}件")
    print(f"別名辞書: {OUT_ALIAS} / {len(alias)}件")
    print(f"確認リスト: {OUT_REVIEW} / {len(review_out)}件")


if __name__ == "__main__":
    main()