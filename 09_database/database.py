# -*- coding: utf-8 -*-
"""
Database Access Layer

Web / AI Engine から SQLite を共通利用するための関数群。
"""

from pathlib import Path
import sqlite3

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB_FILE = ROOT / "09_database" / "ai_platform.db"


def read_table(table_name):
    """テーブル全件取得"""

    conn = sqlite3.connect(DB_FILE)

    try:
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    finally:
        conn.close()

    return df


def get_machine_tables():
    """パチンコ・パチスロの機種テーブルを取得"""

    p_df = read_table("machine_p")
    s_df = read_table("machine_s")

    return p_df, s_df


def get_all_machines():
    """全機種を取得"""

    p_df, s_df = get_machine_tables()

    return pd.concat([p_df, s_df], ignore_index=True)


def search_machines(keyword="", category=None, limit=20, sort="overall_rank"):
    """機種検索"""

    df = get_all_machines()

    if category:
        df = df[df["category"] == category]

    if keyword:
        df = df[
            df["machine_name"]
            .astype(str)
            .str.contains(keyword, case=False, na=False)
        ]

    if sort in df.columns:
        df = df.sort_values(sort)

    return df.head(limit)


def get_machine_by_name(machine_name):
    """機種名で1件取得"""

    df = get_all_machines()

    hit = df[df["machine_name"].astype(str) == machine_name]

    if hit.empty:
        return None

    return hit.iloc[0].to_dict()


def get_halls():
    """ホールAI結果を取得"""

    return read_table("hall")


def get_hall_by_name(hall_name):
    """ホール名で1件取得"""

    df = get_halls()

    hit = df[df["hall_name"].astype(str) == hall_name]

    if hit.empty:
        return None

    return hit.iloc[0].to_dict()