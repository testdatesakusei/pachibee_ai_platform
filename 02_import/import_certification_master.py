# -*- coding: utf-8 -*-
"""
検定通過日マスター取込

output/machine_certification_template.csv
↓
09_database/ai_platform.db
↓
certification_master
"""

from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"
DB_FILE = ROOT / "09_database" / "ai_platform.db"

SRC = OUTPUT / "machine_certification_template.csv"
TABLE_NAME = "certification_master"


def main():
    if not SRC.exists():
        print("入力CSVがありません。")
        print(SRC)
        return

    df = pd.read_csv(SRC)

    required = [
        "machine_name",
        "category",
        "certification_date",
        "certification_source",
        "memo",
    ]

    missing = [c for c in required if c not in df.columns]
    if missing:
        print("不足列があります。")
        print(missing)
        return

    df["certification_date"] = pd.to_datetime(
        df["certification_date"],
        errors="coerce",
    ).dt.strftime("%Y-%m-%d")

    conn = sqlite3.connect(DB_FILE)

    df.to_sql(
        TABLE_NAME,
        conn,
        if_exists="replace",
        index=False,
    )

    conn.close()

    print("取込完了")
    print(f"入力: {SRC}")
    print(f"DB: {DB_FILE}")
    print(f"テーブル: {TABLE_NAME}")
    print(f"件数: {len(df)}")


if __name__ == "__main__":
    main()