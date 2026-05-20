from flask import Blueprint, render_template

bp = Blueprint("setup", __name__, url_prefix="/setup")


@bp.route("/")
def credentials() -> str:
    """Render the credentials configuration form."""
    return render_template("pages/setup.html")
