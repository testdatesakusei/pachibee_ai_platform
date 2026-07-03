# -*- coding: utf-8 -*-
"""
AI Platform Database Builder v1

CSV → SQLite

Machine Intelligence
Hall Intelligence

を1つのDBへ取り込む
"""

from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

OUTPUT = ROOT / "output"

DB_DIR = ROOT / "09_database"

DB_DIR.mkdir(exist_ok=True)

DB_FILE = DB_DIR / "ai_platform.db"


CSV_FILES = {

    "machine_p":

        OUTPUT / "machine_intelligence_v2_P.csv",

    "machine_s":

        OUTPUT / "machine_intelligence_v2_S.csv",

    "hall":

        OUTPUT / "hall_intelligence_v1.csv",

}


def import_csv(cursor, table_name, csv_path):

    if not csv_path.exists():

        print(f"SKIP : {csv_path.name}")

        return

    print(f"IMPORT : {csv_path.name}")

    df = pd.read_csv(csv_path)

    df.to_sql(

        table_name,

        conn,

        if_exists="replace",

        index=False

    )

    print(f"  {len(df)} rows")


print("=" * 50)
print("AI Platform Database Builder")
print("=" * 50)

conn = sqlite3.connect(DB_FILE)

cursor = conn.cursor()

for table_name, csv_path in CSV_FILES.items():

    import_csv(cursor, table_name, csv_path)

conn.commit()

conn.close()

print()
print("完成")
print(DB_FILE)