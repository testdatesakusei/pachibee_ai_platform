from pathlib import Path
import sys

from flask import Blueprint, render_template, request

ROOT = Path(__file__).resolve().parents[2]
DB_DIR = ROOT / "09_database"
sys.path.append(str(DB_DIR))

from database import search_machines  # noqa

search_bp = Blueprint("search", __name__)


SORT_MAP = {
    "overall": "overall_rank",
    "popularity": "active_rank",
    "profit": "profit_rank",
    "lifecycle": "lifecycle_rank",
}


@search_bp.route("/search")
def search():
    keyword = request.args.get("q", "").strip()
    sort_key = request.args.get("sort", "overall")

    sort_column = SORT_MAP.get(sort_key, "overall_rank")

    s_results = search_machines(
        keyword=keyword,
        category="S",
        limit=20,
        sort=sort_column,
    ).to_dict("records")

    p_results = search_machines(
        keyword=keyword,
        category="P",
        limit=20,
        sort=sort_column,
    ).to_dict("records")

    return render_template(
        "search.html",
        q=keyword,
        sort=sort_key,
        s_results=s_results,
        p_results=p_results,
    )