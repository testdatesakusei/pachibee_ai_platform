# -*- coding: utf-8 -*-
"""
検定通過日入力テンプレート作成
"""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"

SRC_P = OUTPUT / "machine_intelligence_v2_P.csv"
SRC_S = OUTPUT / "machine_intelligence_v2_S.csv"
OUT_CSV = OUTPUT / "machine_certification_template.csv"


def main():
    frames = []

    if SRC_P.exists():
        frames.append(pd.read_csv(SRC_P))

    if SRC_S.exists():
        frames.append(pd.read_csv(SRC_S))

    if not frames:
        print("機種CSVが見つかりません。先にMachine Intelligence v2を実行してください。")
        return

    df = pd.concat(frames, ignore_index=True)

    out = df[["machine_name", "category"]].copy()
    out["certification_date"] = ""
    out["certification_source"] = ""
    out["memo"] = ""

    out = out.sort_values(["category", "machine_name"])

    OUTPUT.mkdir(exist_ok=True)
    out.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")

    print("作成完了")
    print(f"出力: {OUT_CSV}")
    print(f"件数: {len(out)}")
    print("certification_date に検定通過日を YYYY-MM-DD 形式で入力します。")


if __name__ == "__main__":
    main()