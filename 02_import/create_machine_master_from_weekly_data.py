# -*- coding: utf-8 -*-
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


BASE_DIR = Path(r"C:\Users\otsuk\Desktop\pachibee_ai_platform")
DB_PATH = BASE_DIR / "09_database" / "ai_platform.db"


def main():
    conn = sqlite3.connect(DB_PATH)

    print("machine_master 作成開始")
    print(f"DB: {DB_PATH}")

    # 既存があれば作り直し
    conn.execute("DROP TABLE IF EXISTS machine_master")

    conn.execute(
        """
        CREATE TABLE machine_master (
            machine_id INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_name TEXT NOT NULL,
            machine_name_normalized TEXT NOT NULL UNIQUE,
            first_seen_date TEXT,
            last_seen_date TEXT,
            data_count INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.execute(
        """
        INSERT INTO machine_master (
            machine_name,
            machine_name_normalized,
            first_seen_date,
            last_seen_date,
            data_count
        )
        SELECT
            machine_name_normalized AS machine_name,
            machine_name_normalized AS machine_name_normalized,
            MIN(data_date) AS first_seen_date,
            MAX(data_date) AS last_seen_date,
            COUNT(*) AS data_count
        FROM weekly_machine_data
        WHERE machine_name_normalized IS NOT NULL
          AND machine_name_normalized != ''
          AND LOWER(machine_name_normalized) != 'nan'
        GROUP BY machine_name_normalized
        ORDER BY first_seen_date, machine_name_normalized
        """
    )

    # weekly_machine_data に machine_id を付与
    conn.execute(
        """
        UPDATE weekly_machine_data
        SET machine_id = (
            SELECT machine_master.machine_id
            FROM machine_master
            WHERE machine_master.machine_name_normalized
                = weekly_machine_data.machine_name_normalized
        )
        """
    )

    conn.commit()

    machine_count = pd.read_sql(
        "SELECT COUNT(*) AS count FROM machine_master",
        conn
    ).iloc[0]["count"]

    linked_count = pd.read_sql(
        """
        SELECT COUNT(*) AS count
        FROM weekly_machine_data
        WHERE machine_id IS NOT NULL
        """,
        conn
    ).iloc[0]["count"]

    total_weekly_count = pd.read_sql(
        "SELECT COUNT(*) AS count FROM weekly_machine_data",
        conn
    ).iloc[0]["count"]

    print("-" * 60)
    print("作成完了")
    print(f"machine_master 件数: {machine_count}")
    print(f"weekly_machine_data 全件数: {total_weekly_count}")
    print(f"machine_id 紐付け済み: {linked_count}")
    print("-" * 60)

    print("機種マスタ先頭20件")
    df = pd.read_sql(
        """
        SELECT
            machine_id,
            machine_name,
            first_seen_date,
            last_seen_date,
            data_count
        FROM machine_master
        ORDER BY machine_id
        LIMIT 20
        """,
        conn
    )

    print(df)

    conn.close()


if __name__ == "__main__":
    main()