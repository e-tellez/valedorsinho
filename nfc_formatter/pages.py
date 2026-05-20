from flask import Blueprint, render_template

bp = Blueprint("nfc_formatter", __name__, url_prefix="/nfc-formatter")


@bp.route("/")
def index() -> str:
    """Render the NFC formatter page."""
    return render_template("pages/nfc_formatter.html")
