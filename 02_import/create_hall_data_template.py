# -*- coding: utf-8 -*-
"""
Hall Intelligence 用 入力CSVテンプレート作成
"""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"
OUT_CSV = OUTPUT / "hall_data_template.csv"


def main():
    OUTPUT.mkdir(exist_ok=True)

    rows = [
        {
            "hall_name": "サンプルホールA",
            "area": "東京都",
            "total_units": 500,
            "pachinko_units": 300,
            "slot_units": 200,
            "avg_operation_score": 88,
            "avg_profit_score": 84,
            "return_score": 72,
            "juggler_score": 91,
            "smart_slot_score": 86,
            "pachinko_score": 74,
            "event_score": 68,
            "new_machine_score": 76,
            "market_score": 70,
            "future_score": 82,
        }
    ]

    df = pd.DataFrame(rows)
    df.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")

    print("作成完了")
    print(f"出力: {OUT_CSV}")
    print(f"件数: {len(df)}")
    print("このCSVを元にホールデータを入力して使います。")


if __name__ == "__main__":
    main()