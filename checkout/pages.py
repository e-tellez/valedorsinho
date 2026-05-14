from flask import Blueprint, Response, request, render_template, session, redirect, url_for

from checkout.config import CLIENT_KEY, ADYEN_ENVIRONMENT
from checkout.helpers import COUNTRY_CURRENCY_MAP
from checkout.integrations import register_integration, get_integrations

bp = Blueprint("pages", __name__)


@bp.route("/", methods=["GET", "POST"])
def index() -> str | Response:
    """Step 1 – collect username and order amount.

    GET  renders the order details form.
    POST validates input, stores values in session, redirects to step 2.
    """
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        amount_raw = request.form.get("amount", "").strip()
        country = request.form.get("country", "MX").upper()

        errors = {}
        amount_warning = None
        if not username:
            errors["error"] = "Please enter a username."
        try:
            amount = float(amount_raw)
            if amount < 0:
                raise ValueError
        except ValueError:
            errors["amount_error"] = "Please enter a valid amount."

        if not errors and amount == 0:
            amount_warning = "Amount is 0 \u2014 this will create a zero-value authorisation to tokenize the card."

        if errors or amount_warning:
            return render_template(
                "pages/order.html",
                form_action="/",
                username=username,
                amount=amount_raw,
                country=country,
                amount_warning=amount_warning,
                **errors,
            )

        country_code, currency = COUNTRY_CURRENCY_MAP.get(country, ("MX", "MXN"))

        session["shopper_reference"] = username
        session["amount_minor_units"] = round(amount * 100)
        session["country_code"] = country_code
        session["currency"] = currency
        return redirect(url_for("pages.select_integration"))

    amount_stored = session.get("amount_minor_units")
    amount_display = "{:.2f}".format(amount_stored / 100) if amount_stored else "10.00"
    return render_template(
        "pages/order.html",
        form_action="/",
        username=session.get("shopper_reference", ""),
        amount=amount_display,
        country=session.get("country_code", "MX"),
        error=None,
        amount_error=None,
    )


@bp.route("/implementations")
def select_integration() -> str | Response:
    """Step 2 – choose an integration type.

    Requires step 1 to have been completed (shopper_reference in session).
    """
    if not session.get("shopper_reference"):
        return redirect(url_for("pages.index"))

    amount_minor_units = session.get("amount_minor_units", 1000)
    return render_template(
        "pages/implementation_index.html",
        shopper_reference=session["shopper_reference"],
        amount=amount_minor_units / 100,
        country_code=session.get("country_code", "MX"),
        currency=session.get("currency", "MXN"),
        integrations=get_integrations(),
    )


@bp.route("/components/checkout")
@register_integration(
    name="Components",
    description="Card fields only \u2014 you control the surrounding UI and pay button.",
    note="(Only Card Component implemented for now)",
    order=2,
)
def components_checkout() -> str | Response:
    """Card Component funnel – Step 3: render the Card Component."""
    if not session.get("shopper_reference"):
        return redirect(url_for("pages.index"))

    session["integration_type"] = "Card Component"
    amount_minor_units = session.get("amount_minor_units", 1000)
    return render_template(
        "pages/card_component.html",
        client_key=CLIENT_KEY,
        environment=ADYEN_ENVIRONMENT,
        shopper_reference=session["shopper_reference"],
        amount_minor_units=amount_minor_units,
        amount=amount_minor_units / 100,
    )


@bp.route("/dropin/checkout")
@register_integration(
    name="Drop-in",
    description="Pre-built UI with all available payment methods in your MA.",
    order=1,
)
def dropin_checkout() -> str | Response:
    """Drop-in funnel – Step 3: render the Drop-in payment form.

    Redirects back to step 1 if the shopper has not entered their details yet.
    """
    if not session.get("shopper_reference"):
        return redirect(url_for("pages.index"))

    session["integration_type"] = "Drop-in"
    amount_minor_units = session.get("amount_minor_units", 1000)
    return render_template(
        "pages/dropin.html",
        client_key=CLIENT_KEY,
        environment=ADYEN_ENVIRONMENT,
        shopper_reference=session["shopper_reference"],
        amount_minor_units=amount_minor_units,
        amount=amount_minor_units / 100,
        country_code=session.get("country_code", "MX"),
        currency=session.get("currency", "MXN"),
    )


@bp.route("/result")
def result() -> str | Response:
    """Render the payment result page and clear the session."""
    payment_result = session.pop("payment_result", None)
    if not payment_result:
        return redirect(url_for("pages.index"))

    integration_type = session.get("integration_type", "Unknown")
    session.clear()

    return render_template(
        "pages/result.html",
        result=payment_result["status"],
        result_code=payment_result["result_code"],
        adyen_response=payment_result["adyen_response"],
        integration_type=integration_type,
    )
