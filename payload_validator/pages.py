from flask import Blueprint, render_template

bp = Blueprint("payload_validator", __name__, url_prefix="/payload-validator")


@bp.route("/")
def index() -> str:
    """Render the payload validator page."""
    return render_template("pages/payload_validator.html")
