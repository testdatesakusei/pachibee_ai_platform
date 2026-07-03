# -*- coding: utf-8 -*-
from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from datetime import datetime

import pandas as pd


BASE_DIR = Path(r"C:\Users\otsuk\Desktop\pachibee_ai_platform")
INPUT_DIR = BASE_DIR / "input" / "weekly_base"
DB_PATH = BASE_DIR / "09_database" / "ai_platform.db"

TARGET_TABLE = "weekly_machine_data"


def parse_date_from_filename(filename: str) -> str | None:
    """
    ベース2025.0122.xlsx → 2025-01-22
    ベース2024.1127(1).xlsx → 2024-11-27
    """
    m = re.search(r"(\d{4})\.(\d{2})(\d{2})", filename)
    if not m:
        return None

    y, mo, d = m.groups()
    try:
        return datetime(int(y), int(mo), int(d)).strftime("%Y-%m-%d")
    except ValueError:
        return None


def clean_col_name(col) -> str:
    if pd.isna(col):
        return ""
    return str(col).strip().replace("\n", "").replace(" ", "").replace("　", "")


def to_number(value):
    if pd.isna(value):
        return None

    s = str(value).strip()
    if s in ["", "-", "ー", "nan", "None"]:
        return None

    s = s.replace(",", "")
    s = s.replace("円", "")
    s = s.replace("%", "")

    try:
        return float(s)
    except ValueError:
        return None


def find_header_row(raw_df: pd.DataFrame) -> int | None:
    """
    機種名を含む行をヘッダー候補にする
    """
    for i in range(min(30, len(raw_df))):
        row_text = " ".join([str(x) for x in raw_df.iloc[i].tolist()])
        if "機種" in row_text:
            return i
    return None


def normalize_machine_name(name: str) -> str:
    if name is None:
        return ""

    s = str(name).strip()
    s = s.replace("　", " ")
    s = re.sub(r"\s+", " ", s)
    s = s.replace("Ｌ ", "L")
    s = s.replace("Ｌ", "L")
    s = s.replace("Ｓ ", "S")
    s = s.replace("Ｓ", "S")
    s = s.replace("Ｐ ", "P")
    s = s.replace("Ｐ", "P")
    return s


def guess_column(columns: list[str], keywords: list[str]) -> str | None:
    for col in columns:
        for kw in keywords:
            if kw in col:
                return col
    return None


def load_machine_master(conn: sqlite3.Connection) -> dict[str, int]:
    """
    machine_master があれば機種名→machine_id の辞書を作る。
    カラム名が多少違っても探す。
    """
    cur = conn.cursor()

    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='machine_master'"
    )
    if not cur.fetchone():
        return {}

    info = pd.read_sql_query("PRAGMA table_info(machine_master)", conn)
    cols = info["name"].tolist()

    id_col = None
    name_col = None

    for c in cols:
        if c.lower() in ["machine_id", "id"]:
            id_col = c
            break

    for c in cols:
        if c in ["machine_name", "name", "機種名"]:
            name_col = c
            break

    if not id_col or not name_col:
        return {}

    df = pd.read_sql_query(
        f"SELECT {id_col} AS machine_id, {name_col} AS machine_name FROM machine_master",
        conn,
    )

    result = {}
    for _, r in df.iterrows():
        name = normalize_machine_name(r["machine_name"])
        if name:
            result[name] = int(r["machine_id"])

    return result


def create_table(conn: sqlite3.Connection):
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {TARGET_TABLE} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            data_date TEXT NOT NULL,
            source_file TEXT NOT NULL,
            sheet_name TEXT NOT NULL,

            machine_id INTEGER,
            machine_name TEXT NOT NULL,
            machine_name_normalized TEXT NOT NULL,

            out_per_unit REAL,
            out_per_player REAL,
            sales_per_unit REAL,
            sales_per_player REAL,
            gross_profit_per_unit REAL,
            gross_profit_per_player REAL,

            unit_count REAL,
            player_count REAL,

            raw_json TEXT,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            UNIQUE(data_date, source_file, sheet_name, machine_name_normalized)
        )
        """
    )

    conn.execute(
        f"CREATE INDEX IF NOT EXISTS idx_{TARGET_TABLE}_date ON {TARGET_TABLE}(data_date)"
    )
    conn.execute(
        f"CREATE INDEX IF NOT EXISTS idx_{TARGET_TABLE}_machine ON {TARGET_TABLE}(machine_name_normalized)"
    )


def extract_sheet_rows(
    file_path: Path,
    sheet_name: str,
    data_date: str,
    machine_map: dict[str, int],
) -> list[dict]:
    raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None, engine="openpyxl")

    header_row = find_header_row(raw)
    if header_row is None:
        return []

    df = pd.read_excel(
        file_path,
        sheet_name=sheet_name,
        header=header_row,
        engine="openpyxl",
    )

    df.columns = [clean_col_name(c) for c in df.columns]
    df = df.dropna(how="all")

    columns = list(df.columns)

    machine_col = guess_column(columns, ["機種名", "機種"])
    if machine_col is None:
        return []

    col_out_unit = guess_column(columns, ["アウト台あたり", "アウト台当り", "アウト/台", "台あたりアウト", "稼"])
    col_out_player = guess_column(columns, ["アウト人あたり", "アウト人当り", "アウト/人", "人あたりアウト"])

    col_sales_unit = guess_column(columns, ["売上台あたり", "売上台当り", "売上/台", "台あたり売上", "売"])
    col_sales_player = guess_column(columns, ["売上人あたり", "売上人当り", "売上/人", "人あたり売上", "売上"])

    col_profit_unit = guess_column(columns, ["粗利台あたり", "粗利台当り", "粗利/台", "台あたり粗利", "粗"])
    col_profit_player = guess_column(columns, ["粗利人あたり", "粗利人当り", "粗利/人", "人あたり粗利"])

    col_units = guess_column(columns, ["台数", "設置台数", "台"])
    col_players = guess_column(columns, ["人数", "遊技人数", "客数"])

    rows = []

    for _, r in df.iterrows():
        machine_name = normalize_machine_name(r.get(machine_col))

        if not machine_name:
            continue

        if machine_name in ["合計", "総計", "平均", "機種名"]:
            continue

        # 機種名っぽくない行を除外
        if len(machine_name) <= 1:
            continue

        machine_id = machine_map.get(machine_name)

        raw_dict = {}
        for c in columns:
            v = r.get(c)
            if pd.isna(v):
                raw_dict[c] = None
            else:
                raw_dict[c] = str(v)

        rows.append(
            {
                "data_date": data_date,
                "source_file": file_path.name,
                "sheet_name": sheet_name,
                "machine_id": machine_id,
                "machine_name": machine_name,
                "machine_name_normalized": machine_name,
                "out_per_unit": to_number(r.get(col_out_unit)) if col_out_unit else None,
                "out_per_player": to_number(r.get(col_out_player)) if col_out_player else None,
                "sales_per_unit": to_number(r.get(col_sales_unit)) if col_sales_unit else None,
                "sales_per_player": to_number(r.get(col_sales_player)) if col_sales_player else None,
                "gross_profit_per_unit": to_number(r.get(col_profit_unit)) if col_profit_unit else None,
                "gross_profit_per_player": to_number(r.get(col_profit_player)) if col_profit_player else None,
                "unit_count": to_number(r.get(col_units)) if col_units else None,
                "player_count": to_number(r.get(col_players)) if col_players else None,
                "raw_json": str(raw_dict),
            }
        )

    return rows


def import_rows(conn: sqlite3.Connection, rows: list[dict]):
    sql = f"""
        INSERT OR REPLACE INTO {TARGET_TABLE} (
            data_date,
            source_file,
            sheet_name,
            machine_id,
            machine_name,
            machine_name_normalized,
            out_per_unit,
            out_per_player,
            sales_per_unit,
            sales_per_player,
            gross_profit_per_unit,
            gross_profit_per_player,
            unit_count,
            player_count,
            raw_json
        )
        VALUES (
            :data_date,
            :source_file,
            :sheet_name,
            :machine_id,
            :machine_name,
            :machine_name_normalized,
            :out_per_unit,
            :out_per_player,
            :sales_per_unit,
            :sales_per_player,
            :gross_profit_per_unit,
            :gross_profit_per_player,
            :unit_count,
            :player_count,
            :raw_json
        )
    """
    conn.executemany(sql, rows)


def main():
    if not INPUT_DIR.exists():
        raise FileNotFoundError(f"入力フォルダがありません: {INPUT_DIR}")

    files = sorted(INPUT_DIR.glob("*.xlsx"))

    print("週次ベースExcel一括取込開始")
    print(f"入力フォルダ: {INPUT_DIR}")
    print(f"DB: {DB_PATH}")
    print(f"対象ファイル数: {len(files)}")
    print("-" * 60)

    if not files:
        print("対象Excelがありません。")
        return

    conn = sqlite3.connect(DB_PATH)
    create_table(conn)

    machine_map = load_machine_master(conn)
    print(f"machine_master照合件数: {len(machine_map)}")
    print("-" * 60)

    total_rows = 0
    total_files = 0
    errors = []

    for file_path in files:
        data_date = parse_date_from_filename(file_path.name)

        if not data_date:
            print(f"SKIP: 日付を取得できません: {file_path.name}")
            continue

        try:
            xls = pd.ExcelFile(file_path, engine="openpyxl")
            file_rows = []

            for sheet_name in xls.sheet_names:
                try:
                    rows = extract_sheet_rows(
                        file_path=file_path,
                        sheet_name=sheet_name,
                        data_date=data_date,
                        machine_map=machine_map,
                    )
                    if rows:
                        file_rows.extend(rows)

                except Exception as e:
                    errors.append([file_path.name, sheet_name, str(e)])

            if file_rows:
                import_rows(conn, file_rows)
                conn.commit()

            total_rows += len(file_rows)
            total_files += 1

            print(f"OK: {file_path.name} / {data_date} / {len(file_rows)}件")

        except Exception as e:
            errors.append([file_path.name, "-", str(e)])
            print(f"ERROR: {file_path.name} / {e}")

    conn.close()

    print("-" * 60)
    print("取込完了")
    print(f"ファイル数: {total_files}")
    print(f"取込件数: {total_rows}")
    print(f"テーブル: {TARGET_TABLE}")

    if errors:
        print("-" * 60)
        print("エラー一覧")
        for e in errors[:50]:
            print(e)


if __name__ == "__main__":
    main()