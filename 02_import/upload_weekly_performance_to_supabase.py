# -*- coding: utf-8 -*-
"""
週次実績CSVをSupabaseへ登録する v1
対象：
- output/weekly_performance_import.csv
- table: machine_weekly_performance

安全設計：
- 500件ずつ分割登録
- NaN/inf除去
- 途中でエラーが出たら停止
"""

from pathlib import Path
import os
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / "config" / ".env"
CSV_PATH = ROOT / "output" / "weekly_performance_import.csv"

load_dotenv(ENV_PATH)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("config/.env に SUPABASE_URL と SUPABASE_KEY が入っていません。")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.replace([np.inf, -np.inf], None)
    df = df.astype(object).where(pd.notna(df), None)
    df = df.replace({"": None, "nan": None, "NaN": None})
    return df


def upload_csv(batch_size: int = 500):
    if not CSV_PATH.exists():
        print(f"CSVがありません: {CSV_PATH}")
        return

    df = pd.read_csv(CSV_PATH)
    df = clean_df(df)

    records = df.to_dict(orient="records")
    total = len(records)

    print("登録開始: machine_weekly_performance")
    print(f"CSV: {CSV_PATH}")
    print(f"件数: {total}")

    for start in range(0, total, batch_size):
        batch = records[start:start + batch_size]
        end = start + len(batch)

        try:
            supabase.table("machine_weekly_performance").insert(batch).execute()
            print(f"  OK: {start + 1} - {end}")
        except Exception as e:
            print(f"  ERROR: {start + 1} - {end}")
            print(e)
            raise

    print("登録完了: machine_weekly_performance")


def main():
    upload_csv()
    print("すべて完了しました。")


if __name__ == "__main__":
    main()