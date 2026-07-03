from flask import Blueprint, render_template, request

hall_bp = Blueprint("hall", __name__)


@hall_bp.route("/hall")
def hall_index():
    q = request.args.get("q", "").strip()

    # まずは土台だけ作る。
    # 後でホールCSV / DBと接続する。
    sample_halls = [
        {
            "hall_name": "サンプルホールA",
            "area": "東京都",
            "ai_score": 86,
            "hall_type": "スマスロ強化型",
            "juggler_score": 78,
            "slot_score": 91,
            "pachinko_score": 72,
        },
        {
            "hall_name": "サンプルホールB",
            "area": "神奈川県",
            "ai_score": 74,
            "hall_type": "バランス型",
            "juggler_score": 82,
            "slot_score": 70,
            "pachinko_score": 77,
        },
    ]

    if q:
        sample_halls = [
            h for h in sample_halls
            if q in h["hall_name"] or q in h["area"]
        ]

    return render_template(
        "hall.html",
        q=q,
        halls=sample_halls,
    )