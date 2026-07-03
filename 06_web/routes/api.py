from pathlib import Path

import pandas as pd
from flask import Blueprint, jsonify, request

api_bp = Blueprint("api", __name__)

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "output"

P_CSV = OUTPUT / "machine_intelligence_v2_P.csv"
S_CSV = OUTPUT / "machine_intelligence_v2_S.csv"


def load_all_data():
    frames = []

    if P_CSV.exists():
        frames.append(pd.read_csv(P_CSV))

    if S_CSV.exists():
        frames.append(pd.read_csv(S_CSV))

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)


@api_bp.route("/api/machine_suggest")
def machine_suggest():
    q = request.args.get("q", "").strip()

    if not q:
        return jsonify([])

    df = load_all_data()

    if df.empty:
        return jsonify([])

    hit = df[
        df["machine_name"]
        .astype(str)
        .str.contains(q, case=False, na=False)
    ].head(10)

    results = []

    for _, row in hit.iterrows():
        results.append({
            "machine_name": row.get("machine_name", ""),
            "category": row.get("category", ""),
            "score": row.get("overall_score_v2", ""),
            "rank": row.get("overall_rank", ""),
        })

    return jsonify(results)