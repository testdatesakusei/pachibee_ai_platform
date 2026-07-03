# -*- coding: utf-8 -*-
"""
市場データ入力テンプレート作成 v1

目的：
- 機種マスターから、中古価格・設置台数を入力するためのCSVテンプレートを作る
- まずは手入力/CSV貼り付けで市場データを追加できる形にする
"""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

MASTER_CSV = ROOT / "output" / "machine_master_v2.csv"
OUT_CSV = ROOT / "output" / "market_data_template.csv"


def main():
    if not MASTER_CSV.exists():
        print("machine_master_v2.csv がありません。")
        return

    df = pd.read_csv(MASTER_CSV)

    out = pd.DataFrame()
    out["machine_id"] = df["machine_id"]
    out["machine_name"] = df["formal_machine_name"]
    out["category"] = df["category"]
    out["maker_name"] = df["maker_name"]
    out["series_name"] = df["series_name"]

    # ここを後から入力する
    out["market_date"] = ""
    out["used_price"] = ""
    out["used_price_change_rate"] = ""
    out["installed_halls"] = ""
    out["installed_units"] = ""
    out["installed_units_change_rate"] = ""
    out["market_memo"] = ""

    out = out.sort_values(["category", "machine_name"])

    out.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")

    print("作成完了")
    print(f"出力: {OUT_CSV}")
    print(f"件数: {len(out)}")
    print("このCSVに中古価格・設置台数を入力して使います。")


if __name__ == "__main__":
    main()