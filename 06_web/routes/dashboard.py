from pathlib import Path

import pandas as pd
from flask import Blueprint, render_template

dashboard_bp = Blueprint("dashboard", __name__)

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "output"

P_CSV = OUTPUT / "machine_intelligence_v2_P.csv"
S_CSV = OUTPUT / "machine_intelligence_v2_S.csv"


def load_data():
    """CSVを読み込む"""

    p_df = pd.read_csv(P_CSV) if P_CSV.exists() else pd.DataFrame()
    s_df = pd.read_csv(S_CSV) if S_CSV.exists() else pd.DataFrame()

    return p_df, s_df


@dashboard_bp.route("/")
def dashboard():

    p_df, s_df = load_data()

    total = len(p_df) + len(s_df)

    return render_template(
        "dashboard.html",
        total=total,
        p_count=len(p_df),
        s_count=len(s_df),
        p_top=p_df.head(20).to_dict("records"),
        s_top=s_df.head(20).to_dict("records"),
    )