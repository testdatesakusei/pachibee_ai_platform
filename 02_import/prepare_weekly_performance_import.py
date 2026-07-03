# -*- coding: utf-8 -*-
"""
週次実績登録用CSV作成 v1
base_excel_import_preview.csv を Supabase の machine_weekly_performance 用に整形する。
まだSupabaseには登録しない安全版。
"""

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "output" / "base_excel_import_preview.csv"
OUT = ROOT / "output" / "weekly_performance_import.csv"


def clean_number(series):
    return pd.to_numeric(series, errors="coerce").replace([np.inf, -np.inf], np.nan)


def main():
    if not SRC.exists():
        print("base_excel_import_preview.csv がありません。先に import_base_excel.py を実行してください。")
        return

    df = pd.read_csv(SRC)

    out = pd.DataFrame()
    out["source_file"] = df.get("source_file")
    out["report_date"] = df.get("report_date")
    out["category"] = df.get("category")
    out["rank"] = None
    out["machine_name"] = df.get("machine_name")
    out["maker_name"] = df.get("maker_name")
    out["spec_ts"] = None
    out["delivery_date"] = None
    out["units"] = None
    out["operation"] = clean_number(df.get("operation"))
    out["sales"] = clean_number(df.get("sales"))
    out["gross_profit"] = clean_number(df.get("gross_profit"))
    out["payout_rate"] = None
    out["unit_price"] = None
    out["unit_profit"] = None
    out["elapsed_week"] = None

    before = len(out)

    out = out.dropna(subset=["source_file", "report_date", "machine_name"])
    out = out.drop_duplicates(subset=["source_file", "report_date", "machine_name", "category"])

    after = len(out)

    out.to_csv(OUT, index=False, encoding="utf-8-sig")

    print("作成完了")
    print(f"元データ: {before}件")
    print(f"出力データ: {after}件")
    print(f"重複/不正除外: {before - after}件")
    print(f"出力先: {OUT}")


if __name__ == "__main__":
    main()