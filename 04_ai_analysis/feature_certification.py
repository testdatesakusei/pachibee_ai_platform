# -*- coding: utf-8 -*-
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

BASE_DIR = Path(r"C:\Users\otsuk\Desktop\pachibee_ai_platform")
DB_PATH = BASE_DIR / "09_database" / "ai_platform.db"


def main():

    conn = sqlite3.connect(DB_PATH)

    print("feature_certification 作成開始")

    feature = pd.read_sql(
        "SELECT * FROM machine_features",
        conn,
    )

    cert = pd.read_sql(
        "SELECT * FROM certification_master",
        conn,
    )

    # certification_master の機種名列を自動取得
    name_col = None
    for c in cert.columns:
        if "machine" in c.lower() and "name" in c.lower():
            name_col = c
            break

    if name_col is None:
        for c in cert.columns:
            if "機種" in c:
                name_col = c
                break

    if name_col is None:
        raise Exception("certification_master に機種名列がありません")

    cert = cert.rename(columns={name_col: "machine_name"})

    # 検定日
    date_col = None
    for c in cert.columns:
        if "certification" in c.lower():
            date_col = c
            break

    if date_col is None:
        for c in cert.columns:
            if "検定" in c:
                date_col = c
                break

    if date_col is not None:

        cert[date_col] = pd.to_datetime(
            cert[date_col],
            errors="coerce",
        )

        feature = feature.merge(
            cert[["machine_name", date_col]],
            on="machine_name",
            how="left",
        )

        feature["certification_date"] = feature[date_col]

        feature["days_from_certification"] = (
            pd.to_datetime(feature["latest_data_date"])
            - feature["certification_date"]
        ).dt.days

        feature["weeks_from_certification"] = (
            feature["days_from_certification"] / 7
        ).round(1)

        feature.drop(columns=[date_col], inplace=True)

    # メーカー
    maker_col = None
    for c in cert.columns:
        if "maker" in c.lower():
            maker_col = c
            break
        if "メーカー" in c:
            maker_col = c
            break

    if maker_col:
        feature = feature.merge(
            cert[["machine_name", maker_col]],
            on="machine_name",
            how="left",
        )
        feature.rename(
            columns={maker_col: "maker"},
            inplace=True,
        )

    # タイプ判定
    feature["is_smart_slot"] = (
        feature["machine_name"].str.startswith("L").astype(int)
    )

    feature["is_smart_pachi"] = (
        feature["machine_name"].str.startswith("e").astype(int)
    )

    feature["is_pachinko"] = (
        feature["machine_name"].str.startswith(("P", "e", "CR", "CRA"))
        .astype(int)
    )

    feature["is_slot"] = (
        1 - feature["is_pachinko"]
    )

    conn.execute(
        "DROP TABLE IF EXISTS machine_features_v2"
    )

    feature.to_sql(
        "machine_features_v2",
        conn,
        if_exists="replace",
        index=False,
    )

    conn.commit()

    print("----------------------------------------")
    print("machine_features_v2 作成完了")
    print(len(feature))

    conn.close()


if __name__ == "__main__":
    main()