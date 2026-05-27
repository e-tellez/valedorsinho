from flask import Blueprint, render_template

bp = Blueprint("terminal_payments", __name__, url_prefix="/terminal-payments")


@bp.route("/")
def index() -> str:
    """Render the Terminal Payments page."""
    return render_template("pages/terminal_payments.html")
