from pathlib import Path

import pandas as pd
from flask import Blueprint, render_template, request

compare_bp = Blueprint("compare", __name__)

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


@compare_bp.route("/compare")
def compare():
    name1 = request.args.get("name1", "").strip()
    name2 = request.args.get("name2", "").strip()

    df = load_all_data()

    machine1 = None
    machine2 = None

    if not df.empty and name1:
        hit1 = df[df["machine_name"].astype(str) == name1]
        if not hit1.empty:
            machine1 = hit1.iloc[0].to_dict()

    if not df.empty and name2:
        hit2 = df[df["machine_name"].astype(str) == name2]
        if not hit2.empty:
            machine2 = hit2.iloc[0].to_dict()

    return render_template(
        "compare.html",
        name1=name1,
        name2=name2,
        machine1=machine1,
        machine2=machine2,
    )