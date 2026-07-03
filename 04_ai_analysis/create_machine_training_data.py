# -*- coding: utf-8 -*-
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


BASE_DIR = Path(r"C:\Users\otsuk\Desktop\pachibee_ai_platform")
DB_PATH = BASE_DIR / "09_database" / "ai_platform.db"
OUTPUT_DIR = BASE_DIR / "output" / "features"


def safe_div(a, b):
    if pd.isna(a) or pd.isna(b) or b == 0:
        return None
    return a / b


def main():
    conn = sqlite3.connect(DB_PATH)

    print("machine_training_data 作成開始")
    print(f"DB: {DB_PATH}")

    df = pd.read_sql(
        """
        SELECT
            w.data_date,
            w.machine_id,
            m.machine_name,
            w.out_per_unit,
            w.sales_per_unit,
            w.gross_profit_per_unit,
            m.first_seen_date
        FROM weekly_machine_data w
        INNER JOIN machine_master m
            ON w.machine_id = m.machine_id
        WHERE w.machine_id IS NOT NULL
          AND LOWER(w.machine_name_normalized) != 'nan'
        ORDER BY w.machine_id, w.data_date
        """,
        conn,
    )

    df["data_date"] = pd.to_datetime(df["data_date"])
    df["first_seen_date"] = pd.to_datetime(df["first_seen_date"])

    for col in ["out_per_unit", "sales_per_unit", "gross_profit_per_unit"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    rows = []

    for machine_id, g in df.groupby("machine_id"):
        g = g.sort_values("data_date").copy()
        g = g.reset_index(drop=True)

        machine_name = g.loc[0, "machine_name"]
        first_seen = g.loc[0, "first_seen_date"]

        g["week_index"] = range(len(g))
        g["weeks_from_first_seen"] = (
            (g["data_date"] - first_seen).dt.days // 7
        ).astype(int)

        g["avg_out_4w"] = g["out_per_unit"].rolling(4, min_periods=2).mean()
        g["avg_out_12w"] = g["out_per_unit"].rolling(12, min_periods=4).mean()
        g["avg_out_26w"] = g["out_per_unit"].rolling(26, min_periods=8).mean()

        g["avg_sales_4w"] = g["sales_per_unit"].rolling(4, min_periods=2).mean()
        g["avg_profit_4w"] = g["gross_profit_per_unit"].rolling(4, min_periods=2).mean()

        g["peak_out_so_far"] = g["out_per_unit"].cummax()
        g["peak_ratio_now"] = g.apply(
            lambda r: safe_div(r["out_per_unit"], r["peak_out_so_far"]),
            axis=1,
        )

        g["diff_out_1w"] = g["out_per_unit"].diff(1)
        g["diff_out_4w"] = g["out_per_unit"] - g["out_per_unit"].shift(4)

        g["target_out_next_1w"] = g["out_per_unit"].shift(-1)
        g["target_out_next_4w"] = g["out_per_unit"].shift(-4)
        g["target_out_next_12w"] = g["out_per_unit"].shift(-12)

        g["target_change_4w"] = g["target_out_next_4w"] - g["out_per_unit"]
        g["target_change_rate_4w"] = g.apply(
            lambda r: safe_div(r["target_change_4w"], r["out_per_unit"]),
            axis=1,
        )

        use_cols = [
            "data_date",
            "machine_id",
            "machine_name",
            "week_index",
            "weeks_from_first_seen",
            "out_per_unit",
            "sales_per_unit",
            "gross_profit_per_unit",
            "avg_out_4w",
            "avg_out_12w",
            "avg_out_26w",
            "avg_sales_4w",
            "avg_profit_4w",
            "peak_out_so_far",
            "peak_ratio_now",
            "diff_out_1w",
            "diff_out_4w",
            "target_out_next_1w",
            "target_out_next_4w",
            "target_out_next_12w",
            "target_change_4w",
            "target_change_rate_4w",
        ]

        rows.append(g[use_cols])

    train_df = pd.concat(rows, ignore_index=True)

    # 学習に使いやすいよう、最低限の欠損除外
    train_df_model = train_df.dropna(
        subset=[
            "out_per_unit",
            "avg_out_4w",
            "avg_out_12w",
            "peak_ratio_now",
            "target_out_next_4w",
        ]
    ).copy()

    conn.execute("DROP TABLE IF EXISTS machine_training_data")
    train_df.to_sql(
        "machine_training_data",
        conn,
        if_exists="replace",
        index=False,
    )

    conn.execute("DROP TABLE IF EXISTS machine_training_data_model")
    train_df_model.to_sql(
        "machine_training_data_model",
        conn,
        if_exists="replace",
        index=False,
    )

    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_training_machine_id ON machine_training_data(machine_id)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_training_date ON machine_training_data(data_date)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_training_model_machine_id ON machine_training_data_model(machine_id)"
    )

    conn.commit()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    out_csv = OUTPUT_DIR / "machine_training_data_model.csv"
    train_df_model.to_csv(out_csv, index=False, encoding="utf-8-sig")

    print("-" * 60)
    print("作成完了")
    print(f"machine_training_data 件数: {len(train_df)}")
    print(f"machine_training_data_model 件数: {len(train_df_model)}")
    print(f"CSV出力: {out_csv}")
    print("-" * 60)

    print("学習用データ 先頭20件")
    print(
        train_df_model[
            [
                "data_date",
                "machine_id",
                "machine_name",
                "out_per_unit",
                "avg_out_4w",
                "avg_out_12w",
                "peak_ratio_now",
                "target_out_next_4w",
                "target_change_rate_4w",
            ]
        ]
        .head(20)
        .to_string(index=False)
    )

    conn.close()


if __name__ == "__main__":
    main()