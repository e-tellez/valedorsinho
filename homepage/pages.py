from flask import Blueprint, render_template

bp = Blueprint("homepage", __name__)


@bp.route("/")
def dashboard() -> str:
    """Render the main dashboard with all tool cards."""
    return render_template("pages/dashboard.html")
