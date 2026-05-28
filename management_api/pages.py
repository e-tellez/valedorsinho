from flask import Blueprint, render_template

bp = Blueprint("management_api", __name__, url_prefix="/management-api")


@bp.route("/")
def index() -> str:
    """Render the Management API page."""
    return render_template("pages/management_api.html")
