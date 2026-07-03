# -*- coding: utf-8 -*-
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


BASE_DIR = Path(r"C:\Users\otsuk\Desktop\pachibee_ai_platform")
DB_PATH = BASE_DIR / "09_database" / "ai_platform.db"
OUTPUT_DIR = BASE_DIR / "output" / "predictions"

FEATURE_COLS = [
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
]

TARGET_COL = "target_out_next_4w"


def main():
    conn = sqlite3.connect(DB_PATH)

    print("稼働予測モデル 作成開始")
    print(f"DB: {DB_PATH}")

    df = pd.read_sql("SELECT * FROM machine_training_data_model", conn)

    print(f"学習データ件数: {len(df)}")

    for col in FEATURE_COLS + [TARGET_COL]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=FEATURE_COLS + [TARGET_COL]).copy()

    print(f"欠損除外後: {len(df)}")

    try:
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.metrics import mean_absolute_error, r2_score
        from sklearn.model_selection import train_test_split
    except ImportError:
        print("scikit-learn がありません。以下を実行してください。")
        print("py -m pip install scikit-learn")
        conn.close()
        return

    X = df[FEATURE_COLS]
    y = df[TARGET_COL]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
    )

    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42,
        n_jobs=-1,
        min_samples_leaf=3,
    )

    model.fit(X_train, y_train)

    pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, pred)
    r2 = r2_score(y_test, pred)

    print("-" * 60)
    print("モデル評価")
    print(f"MAE 平均誤差: {mae:,.0f}")
    print(f"R2 決定係数: {r2:.3f}")

    latest_df = pd.read_sql(
        """
        SELECT
            f.machine_id,
            f.machine_name,
            f.weeks_from_first_seen,
            f.latest_out_per_unit AS out_per_unit,
            f.latest_sales_per_unit AS sales_per_unit,
            f.latest_profit_per_unit AS gross_profit_per_unit,
            f.avg_out_4w,
            f.avg_out_12w,
            f.avg_out_26w,
            f.avg_sales_4w,
            f.avg_profit_4w,
            f.peak_out_per_unit AS peak_out_so_far,
            f.peak_ratio AS peak_ratio_now,
            f.trend,
            f.life_stage,
            f.operation_score,
            f.latest_data_date
        FROM machine_features f
        """,
        conn,
    )

    hist = pd.read_sql(
        """
        SELECT
            machine_id,
            data_date,
            out_per_unit
        FROM weekly_machine_data
        WHERE machine_id IS NOT NULL
        ORDER BY machine_id, data_date
        """,
        conn,
    )

    hist["out_per_unit"] = pd.to_numeric(hist["out_per_unit"], errors="coerce")

    diff_rows = []

    for machine_id, g in hist.groupby("machine_id"):
        g = g.sort_values("data_date").copy()
        latest_out = g["out_per_unit"].iloc[-1]
        prev_1 = g["out_per_unit"].iloc[-2] if len(g) >= 2 else None
        prev_4 = g["out_per_unit"].iloc[-5] if len(g) >= 5 else None

        diff_rows.append(
            {
                "machine_id": machine_id,
                "diff_out_1w": latest_out - prev_1 if prev_1 is not None else None,
                "diff_out_4w": latest_out - prev_4 if prev_4 is not None else None,
            }
        )

    diff_df = pd.DataFrame(diff_rows)
    latest_df = latest_df.merge(diff_df, on="machine_id", how="left")

    for col in FEATURE_COLS:
        latest_df[col] = pd.to_numeric(latest_df[col], errors="coerce")

    predict_df = latest_df.dropna(subset=FEATURE_COLS).copy()

    predict_df["pred_out_4w"] = model.predict(predict_df[FEATURE_COLS])
    predict_df["pred_change_4w"] = predict_df["pred_out_4w"] - predict_df["out_per_unit"]
    predict_df["pred_change_rate_4w"] = (
        predict_df["pred_change_4w"] / predict_df["out_per_unit"]
    )

    def judge_prediction(rate):
        if pd.isna(rate):
            return "判定不可"
        if rate >= 0.10:
            return "上昇予測"
        if rate >= 0.03:
            return "微増予測"
        if rate >= -0.03:
            return "横ばい予測"
        if rate >= -0.10:
            return "微減予測"
        return "下降予測"

    predict_df["prediction_judge"] = predict_df["pred_change_rate_4w"].apply(
        judge_prediction
    )

    result_cols = [
        "machine_id",
        "machine_name",
        "latest_data_date",
        "out_per_unit",
        "avg_out_4w",
        "pred_out_4w",
        "pred_change_4w",
        "pred_change_rate_4w",
        "prediction_judge",
        "trend",
        "life_stage",
        "operation_score",
    ]

    result_df = predict_df[result_cols].copy()
    result_df["pred_out_4w"] = result_df["pred_out_4w"].round(0)
    result_df["pred_change_4w"] = result_df["pred_change_4w"].round(0)
    result_df["pred_change_rate_4w"] = result_df["pred_change_rate_4w"].round(4)

    conn.execute("DROP TABLE IF EXISTS operation_predictions")

    result_df.to_sql(
        "operation_predictions",
        conn,
        if_exists="replace",
        index=False,
    )

    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_operation_predictions_machine_id
        ON operation_predictions(machine_id)
        """
    )

    conn.commit()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    out_csv = OUTPUT_DIR / "operation_predictions.csv"
    result_df.to_csv(out_csv, index=False, encoding="utf-8-sig")

    print("-" * 60)
    print("予測完了")
    print(f"予測件数: {len(result_df)}")
    print(f"CSV出力: {out_csv}")

    print("-" * 60)
    print("4週後 上昇予測 上位20件")
    print(
        result_df.sort_values("pred_change_rate_4w", ascending=False)
        .head(20)[
            [
                "machine_id",
                "machine_name",
                "out_per_unit",
                "pred_out_4w",
                "pred_change_rate_4w",
                "prediction_judge",
                "life_stage",
            ]
        ]
        .to_string(index=False)
    )

    print("-" * 60)
    print("4週後 下降予測 上位20件")
    print(
        result_df.sort_values("pred_change_rate_4w", ascending=True)
        .head(20)[
            [
                "machine_id",
                "machine_name",
                "out_per_unit",
                "pred_out_4w",
                "pred_change_rate_4w",
                "prediction_judge",
                "life_stage",
            ]
        ]
        .to_string(index=False)
    )

    conn.close()


if __name__ == "__main__":
    main()