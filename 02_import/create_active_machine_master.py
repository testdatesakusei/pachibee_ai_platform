# -*- coding: utf-8 -*-
from __future__ import annotations

import sqlite3
from pathlib import Path
import pandas as pd

BASE_DIR = Path(r"C:\Users\otsuk\Desktop\pachibee_ai_platform")
DB_PATH = BASE_DIR / "09_database" / "ai_platform.db"
OUTPUT_DIR = BASE_DIR / "output" / "features"


def main():
    conn = sqlite3.connect(DB_PATH)

    print("active_machine_master 作成開始")

    latest_date = pd.read_sql("""
        SELECT MAX(data_date) AS latest_date
        FROM weekly_machine_data
        WHERE machine_id IS NOT NULL
    """, conn).iloc[0]["latest_date"]

    print(f"最新データ日: {latest_date}")

    df = pd.read_sql("""
        SELECT
            machine_id,
            machine_name,
            machine_name_normalized,
            first_seen_date,
            last_seen_date,
            data_count
        FROM machine_master
        WHERE machine_name_normalized IS NOT NULL
          AND LOWER(machine_name_normalized) != 'nan'
    """, conn)

    df["first_seen_date"] = pd.to_datetime(df["first_seen_date"])
    df["last_seen_date"] = pd.to_datetime(df["last_seen_date"])
    latest_dt = pd.to_datetime(latest_date)

    df["days_since_last_seen"] = (latest_dt - df["last_seen_date"]).dt.days
    df["weeks_since_last_seen"] = (df["days_since_last_seen"] / 7).round(1)

    # 現役扱い：最新日から104週以内に登場している機種
    active_df = df[df["days_since_last_seen"] <= 104 * 7].copy()

    active_df["active_status"] = active_df["days_since_last_seen"].apply(
        lambda x: "現役" if x <= 28 else "準現役"
    )

    conn.execute("DROP TABLE IF EXISTS active_machine_master")
    active_df.to_sql(
        "active_machine_master",
        conn,
        if_exists="replace",
        index=False,
    )

    conn.commit()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = OUTPUT_DIR / "active_machine_master.csv"
    active_df.to_csv(out_csv, index=False, encoding="utf-8-sig")

    print("作成完了")
    print(f"全機種数: {len(df)}")
    print(f"現役対象機種数: {len(active_df)}")
    print(f"CSV出力: {out_csv}")
    print(
        active_df.sort_values("last_seen_date", ascending=False)
        .head(30)
        .to_string(index=False)
    )

    conn.close()


if __name__ == "__main__":
    main()