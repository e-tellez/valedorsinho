from flask import Blueprint, render_template

from checkout.config import MERCHANT_ACCOUNT

bp = Blueprint("terminal_fleet", __name__, url_prefix="/terminal-fleet")


@bp.route("/")
def index() -> str:
    """Render the Terminal Fleet Manager page."""
    return render_template(
        "pages/terminal_fleet.html",
        merchant_account=MERCHANT_ACCOUNT,
    )
