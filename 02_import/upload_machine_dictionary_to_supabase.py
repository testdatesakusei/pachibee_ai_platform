# -*- coding: utf-8 -*-
"""
機種辞書CSVをSupabaseへ登録する v1
安全版：
- CSV 3種類を登録
- 500件ずつ分割登録
- エラーが出たら止めて内容を表示
"""

from pathlib import Path
import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / "config" / ".env"
OUT_DIR = ROOT / "output"

load_dotenv(ENV_PATH)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("config/.env に SUPABASE_URL と SUPABASE_KEY が入っていません。")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    import numpy as np

    df = df.copy()

    # inf / -inf をNoneに変換
    df = df.replace([np.inf, -np.inf], None)

    # NaNをNoneに変換
    df = df.astype(object).where(pd.notna(df), None)

    # 空文字もNoneに寄せる
    df = df.replace({"": None, "nan": None, "NaN": None})

    return df


def upload_csv(csv_name: str, table_name: str, batch_size: int = 500):
    path = OUT_DIR / csv_name

    if not path.exists():
        print(f"ファイルがありません: {path}")
        return

    df = pd.read_csv(path)
    df = clean_df(df)

    records = df.to_dict(orient="records")
    total = len(records)

    print(f"\n登録開始: {table_name}")
    print(f"CSV: {csv_name}")
    print(f"件数: {total}")

    for start in range(0, total, batch_size):
        batch = records[start:start + batch_size]
        end = start + len(batch)

        try:
            supabase.table(table_name).insert(batch).execute()
            print(f"  OK: {start + 1} - {end}")
        except Exception as e:
            print(f"  ERROR: {start + 1} - {end}")
            print(e)
            raise

    print(f"登録完了: {table_name}")


def main():
    upload_csv("machine_dictionary_import.csv", "machine_dictionary")
    upload_csv("machine_alias_import.csv", "machine_alias")
    upload_csv("machine_classification_review.csv", "machine_classification_review")

    print("\nすべて完了しました。")


if __name__ == "__main__":
    main()