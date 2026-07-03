# -*- coding: utf-8 -*-
from __future__ import annotations

import sqlite3
from pathlib import Path
from difflib import SequenceMatcher

import pandas as pd


BASE_DIR = Path(r"C:\Users\otsuk\Desktop\pachibee_ai_platform")
DB_PATH = BASE_DIR / "09_database" / "ai_platform.db"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_CSV = OUTPUT_DIR / "machine_name_review.csv"


def normalize_name(s: str) -> str:
    if s is None:
        return ""

    s = str(s).strip()
    s = s.replace("　", "")
    s = s.replace(" ", "")
    s = s.upper()

    replacements = {
        "Ｌ": "L",
        "Ｓ": "S",
        "Ｐ": "P",
        "ＣＲ": "CR",
        "ＰＡ": "PA",
        "ＰＦ": "PF",
        "スマスロ": "L",
        "パチスロ": "",
        "ぱちスロ": "",
        "ぱちんこ": "",
        "パチンコ": "",
        "～": "",
        "〜": "",
        "-": "",
        "－": "",
        "―": "",
        "・": "",
        " ": "",
        "　": "",
    }

    for k, v in replacements.items():
        s = s.replace(k, v)

    return s


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def get_cert_name_column(conn: sqlite3.Connection) -> str:
    info = pd.read_sql("PRAGMA table_info(certification_master)", conn)
    cols = info["name"].tolist()

    for c in ["machine_name", "name", "機種名"]:
        if c in cols:
            return c

    raise Exception(f"certification_master に機種名カラムが見つかりません: {cols}")


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)

    print("機種名 名寄せチェック表 作成開始")
    print(f"DB: {DB_PATH}")

    machine_df = pd.read_sql(
        """
        SELECT
            machine_id,
            machine_name,
            first_seen_date,
            last_seen_date,
            data_count
        FROM machine_master
        ORDER BY machine_id
        """,
        conn,
    )

    cert_col = get_cert_name_column(conn)

    cert_df = pd.read_sql(
        f"""
        SELECT
            {cert_col} AS cert_machine_name,
            certification_date
        FROM certification_master
        """,
        conn,
    )

    conn.close()

    machine_df["norm"] = machine_df["machine_name"].apply(normalize_name)
    cert_df["norm"] = cert_df["cert_machine_name"].apply(normalize_name)

    results = []

    for _, m in machine_df.iterrows():
        m_norm = m["norm"]

        best_name = ""
        best_date = ""
        best_score = 0.0

        for _, c in cert_df.iterrows():
            c_norm = c["norm"]
            score = similarity(m_norm, c_norm)

            if score > best_score:
                best_score = score
                best_name = c["cert_machine_name"]
                best_date = c["certification_date"]

        judge = "確認"
        if best_score >= 0.98:
            judge = "ほぼ一致"
        elif best_score >= 0.90:
            judge = "候補"
        elif best_score >= 0.80:
            judge = "要確認"
        else:
            judge = "未一致"

        results.append(
            {
                "machine_id": m["machine_id"],
                "machine_name": m["machine_name"],
                "first_seen_date": m["first_seen_date"],
                "last_seen_date": m["last_seen_date"],
                "data_count": m["data_count"],
                "best_cert_machine_name": best_name,
                "certification_date": best_date,
                "similarity": round(best_score, 4),
                "judge": judge,
                "final_machine_name": "",
                "memo": "",
            }
        )

    out_df = pd.DataFrame(results)

    out_df = out_df.sort_values(
        by=["judge", "similarity", "machine_name"],
        ascending=[True, False, True],
    )

    out_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    print("-" * 60)
    print("作成完了")
    print(f"出力: {OUTPUT_CSV}")
    print(f"件数: {len(out_df)}")
    print("-" * 60)

    print("判定別件数")
    print(out_df["judge"].value_counts())

    print("-" * 60)
    print("未一致・要確認 先頭30件")
    print(
        out_df[out_df["judge"].isin(["未一致", "要確認"])]
        .head(30)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()