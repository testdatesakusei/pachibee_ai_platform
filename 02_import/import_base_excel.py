# -*- coding: utf-8 -*-
"""
ベースExcel自動取込スクリプト v2
重要ルール：
- Sheet1 = パチンコ
- Sheet2 = パチスロ
"""

from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BASE_DIR = ROOT / "base_files"
OUT_DIR = ROOT / "output"
OUT_DIR.mkdir(exist_ok=True)

def detect_report_date(filename: str):
    m = re.search(r"ベース(\d{4})\.(\d{4})", filename)
    if not m:
        return None
    y = m.group(1)
    md = m.group(2)
    return f"{y}-{md[:2]}-{md[2:]}"

def normalize_columns(cols):
    return [str(c).replace("\n", "").replace(" ", "").strip() for c in cols]

def find_col(cols, keywords):
    for c in cols:
        s = str(c)
        if all(k in s for k in keywords):
            return c
    return None

def read_base_file(path: Path):
    report_date = detect_report_date(path.name)
    rows = []

    try:
        xls = pd.ExcelFile(path)
    except Exception as e:
        print(f"開けません: {path.name} / {e}")
        return rows

    # Sheet1=パチンコ、Sheet2=パチスロ固定
    for sheet_index, sheet in enumerate(xls.sheet_names[:2]):
        category = "P" if sheet_index == 0 else "S"

        try:
            raw = pd.read_excel(path, sheet_name=sheet, header=None)
        except Exception:
            continue

        header_candidates = []
        for i in range(min(len(raw), 80)):
            text = " ".join([str(x) for x in raw.iloc[i].tolist() if pd.notna(x)])
            if "機種" in text and ("稼" in text or "動" in text):
                header_candidates.append(i)

        for header_row in header_candidates:
            try:
                df = pd.read_excel(path, sheet_name=sheet, header=header_row)
                df.columns = normalize_columns(df.columns)
            except Exception:
                continue

            machine_col = find_col(df.columns, ["機種"])
            op_col = find_col(df.columns, ["稼"])
            sales_col = find_col(df.columns, ["売"])
            profit_col = find_col(df.columns, ["粗"])
            maker_col = find_col(df.columns, ["メーカー"])

            if machine_col is None or op_col is None:
                continue

            for _, r in df.iterrows():
                machine = r.get(machine_col)
                if pd.isna(machine):
                    continue

                machine = str(machine).strip()
                if machine in ["", "機種名", "nan", "None"]:
                    continue
                if "機種" in machine and len(machine) <= 6:
                    continue

                rows.append({
                    "source_file": path.name,
                    "report_date": report_date,
                    "sheet_name": sheet,
                    "sheet_index": sheet_index + 1,
                    "category": category,
                    "machine_name": machine,
                    "maker_name": None if maker_col is None or pd.isna(r.get(maker_col)) else str(r.get(maker_col)).strip(),
                    "operation": r.get(op_col),
                    "sales": None if sales_col is None else r.get(sales_col),
                    "gross_profit": None if profit_col is None else r.get(profit_col),
                })

            break

    return rows

def main():
    files = sorted(BASE_DIR.glob("ベース*.xlsx"))
    if not files:
        print("base_files フォルダに ベース*.xlsx がありません。")
        return

    all_rows = []
    for f in files:
        print(f"読み込み中: {f.name}")
        all_rows.extend(read_base_file(f))

    out = pd.DataFrame(all_rows)
    out_path = OUT_DIR / "base_excel_import_preview.csv"
    out.to_csv(out_path, index=False, encoding="utf-8-sig")

    print(f"完了: {len(out)} 行")
    print(out["category"].value_counts(dropna=False))
    print(f"出力: {out_path}")

if __name__ == "__main__":
    main()