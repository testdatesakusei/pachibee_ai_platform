# -*- coding: utf-8 -*-
"""
稼働予測サンプル v1
output/base_excel_import_preview.csv を使って、直近重視のランキングを作ります。
"""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "output"
SRC = OUT_DIR / "base_excel_import_preview.csv"

def main():
    if not SRC.exists():
        print("先に 02_import/import_base_excel.py を実行してください。")
        return

    df = pd.read_csv(SRC)
    df["operation"] = pd.to_numeric(df["operation"], errors="coerce")
    df["report_date"] = pd.to_datetime(df["report_date"], errors="coerce")
    df = df.dropna(subset=["machine_name", "operation"])

    df = df.sort_values(["machine_name", "report_date"])

    latest = df.groupby(["category", "machine_name"], as_index=False).tail(1)
    avg = df.groupby(["category", "machine_name"], as_index=False)["operation"].mean().rename(columns={"operation": "avg_operation"})
    maxv = df.groupby(["category", "machine_name"], as_index=False)["operation"].max().rename(columns={"operation": "max_operation"})
    cnt = df.groupby(["category", "machine_name"], as_index=False)["operation"].count().rename(columns={"operation": "data_count"})

    summary = latest[["category", "machine_name", "operation"]].rename(columns={"operation": "latest_operation"})
    summary = summary.merge(avg, on=["category", "machine_name"], how="left")
    summary = summary.merge(maxv, on=["category", "machine_name"], how="left")
    summary = summary.merge(cnt, on=["category", "machine_name"], how="left")

    summary["predicted_operation"] = (
        summary["latest_operation"] * 0.65 +
        summary["avg_operation"] * 0.25 +
        summary["max_operation"] * 0.10
    )

    for c in ["P", "S"]:
        out = summary[summary["category"] == c].sort_values("predicted_operation", ascending=False).head(50)
        out_path = OUT_DIR / f"forecast_top50_{c}.csv"
        out.to_csv(out_path, index=False, encoding="utf-8-sig")
        print(f"{c} 出力: {out_path}")

if __name__ == "__main__":
    main()
