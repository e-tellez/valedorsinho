from flask import Blueprint, render_template

bp = Blueprint("terminal_payments", __name__, url_prefix="/terminal-payments")


@bp.route("/")
def index() -> str:
    """Render the Terminal Payments page."""
    return render_template("pages/terminal_payments.html")


@bp.route("/make-payment")
def make_payment() -> str:
    """Render the Make a Payment placeholder."""
    return render_template("pages/terminal_make_payment.html")


@bp.route("/nfc")
def nfc_flow() -> str:
    """Render the NFC flow placeholder."""
    return render_template("pages/terminal_nfc.html")


@bp.route("/card-acquisition")
def card_acquisition() -> str:
    """Render the Card Acquisition flow placeholder."""
    return render_template("pages/terminal_card_acquisition.html")


@bp.route("/auth-capt")
def auth_capt() -> str:
    """Render the Auth-Capt flow placeholder."""
    return render_template("pages/terminal_auth_capt.html")
