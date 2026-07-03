from pathlib import Path

import pandas as pd
from flask import Blueprint, render_template, request

machine_bp = Blueprint("machine", __name__)

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


@machine_bp.route("/machine")
def machine_detail():
    machine_name = request.args.get("name", "").strip()

    df = load_all_data()

    if df.empty or not machine_name:
        return render_template(
            "machine.html",
            machine=None,
            message="機種が見つかりません。",
        )

    hit = df[df["machine_name"].astype(str) == machine_name]

    if hit.empty:
        return render_template(
            "machine.html",
            machine=None,
            message="機種が見つかりません。",
        )

    machine = hit.iloc[0].to_dict()

    return render_template(
        "machine.html",
        machine=machine,
        message=None,
    )