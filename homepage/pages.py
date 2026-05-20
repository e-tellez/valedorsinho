from flask import Blueprint, render_template

bp = Blueprint("homepage", __name__)


@bp.route("/")
def dashboard() -> str:
    """Render the main dashboard with all tool cards."""
    return render_template("pages/dashboard.html")


# ---------------------------------------------------------------------------
# Placeholder routes – each will be replaced by its own blueprint/logic later
# ---------------------------------------------------------------------------

@bp.route("/setup-placeholder")
def setup_placeholder() -> str:
    """Placeholder for the setup/credentials page."""
    return render_template(
        "pages/placeholder.html",
        title="Set Up",
        description="Configure Adyen credentials and environment settings. This feature is under development.",
    )


@bp.route("/payload-validator")
def payload_validator() -> str:
    """Placeholder for the payment payload validator."""
    return render_template(
        "pages/placeholder.html",
        title="Payment Payload Validator",
        description="Validate /payments payloads against OpenAPI specs. This feature is under development.",
    )


@bp.route("/payload-suggested")
def payload_suggested() -> str:
    """Placeholder for the suggested payload generator."""
    return render_template(
        "pages/placeholder.html",
        title="Payload Suggested",
        description="Generate recommended payloads per merchant vertical. This feature is under development.",
    )


@bp.route("/nfc-formatter")
def nfc_formatter() -> str:
    """Placeholder for the NFC credential formatter."""
    return render_template(
        "pages/placeholder.html",
        title="NFC Formatter",
        description="Configure NFC credentials for merchant tap-to-pay. This feature is under development.",
    )


@bp.route("/webhook-logs")
def webhook_logs() -> str:
    """Placeholder for the webhook log viewer."""
    return render_template(
        "pages/placeholder.html",
        title="Webhook Logs",
        description="Monitor incoming webhook notifications in real time. This feature is under development.",
    )
