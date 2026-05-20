from flask import Blueprint, render_template

bp = Blueprint("homepage", __name__)


@bp.route("/")
def dashboard() -> str:
    """Render the main dashboard with all tool cards."""
    return render_template("pages/dashboard.html")


# ---------------------------------------------------------------------------
# Placeholder routes – each will be replaced by its own blueprint/logic later
# ---------------------------------------------------------------------------

@bp.route("/webhook-logs")
def webhook_logs() -> str:
    """Placeholder for the webhook log viewer."""
    return render_template(
        "pages/placeholder.html",
        title="Webhook Logs",
        description="Monitor incoming webhook notifications in real time. This feature is under development.",
    )
