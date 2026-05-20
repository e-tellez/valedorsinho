from flask import Blueprint, render_template

from payload_suggested.verticals import VERTICALS

bp = Blueprint("payload_suggested", __name__, url_prefix="/payload-suggested")


@bp.route("/")
def index() -> str:
    """Render the payload suggested page with vertical checkboxes."""
    return render_template(
        "pages/payload_suggested.html",
        verticals=VERTICALS,
    )
