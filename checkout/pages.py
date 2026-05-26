from dataclasses import asdict

from flask import Blueprint, Response, request, render_template, session, redirect, url_for

from checkout.checkout_helpers import COUNTRY_CURRENCY_MAP, build_checkout_context, require_session
from checkout.integrations import register_integration, get_integrations, get_integration_categories
from checkout.contexts import OrderFormContext, PaymentResult

bp = Blueprint("pages", __name__)


@bp.route("/checkout")
def index() -> str | Response:
    """Step 1 – choose between guest and account checkout flows."""
    return render_template("pages/choose_flow.html")


@bp.route("/order", methods=["GET", "POST"])
def order() -> str | Response:
    """Step 2 – collect order details (and username for the account flow).

    GET  renders the order form.
    POST validates input, stores values in session, redirects to step 3.
    """
    flow_param = request.args.get("flow")
    if flow_param is not None:
        is_guest = flow_param == "guest"
        session["is_guest"] = is_guest
    else:
        is_guest = session.get("is_guest", False)

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        amount_raw = request.form.get("amount", "").strip()
        country = request.form.get("country", "MX").upper()
        is_guest = request.form.get("is_guest") == "true"

        errors = {}
        amount_warning = None
        if not is_guest and not username:
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
            order_form_context = OrderFormContext(
                form_action="/order",
                is_guest=is_guest,
                username=username,
                amount=amount_raw,
                country=country,
                amount_warning=amount_warning,
                error=errors.get("error"),
                amount_error=errors.get("amount_error"),
            )
            return render_template("pages/order.html", **asdict(order_form_context))

        currency = COUNTRY_CURRENCY_MAP.get(country, "MXN")
        country_code = country

        session["is_guest"] = is_guest
        session["shopper_reference"] = username if not is_guest else ""
        session["amount_minor_units"] = round(amount * 100)
        session["country_code"] = country_code
        session["currency"] = currency
        return redirect(url_for("pages.select_integration"))

    amount_stored = session.get("amount_minor_units")
    amount_display = "{:.2f}".format(amount_stored / 100) if amount_stored else "10.00"
    order_form_context = OrderFormContext(
        form_action="/order",
        is_guest=is_guest,
        username=session.get("shopper_reference", ""),
        amount=amount_display,
        country=session.get("country_code", "MX"),
    )
    return render_template("pages/order.html", **asdict(order_form_context))


@bp.route("/implementations")
@require_session
def select_integration() -> str | Response:
    """Step 2 – choose an integration type.

    Requires step 1 to have been completed (shopper_reference in session).
    """

    checkout_context = build_checkout_context()
    return render_template(
        "pages/implementation_index.html",
        **asdict(checkout_context),
        integrations=get_integrations(),
        categories=get_integration_categories(),
    )


@bp.route("/components/checkout")
@register_integration(
    name="Components",
    description="Card fields only \u2014 you control the surrounding UI and pay button.",
    note="(Only Card Component implemented for now)",
    order=2,
)
@require_session
def components_checkout() -> str | Response:
    """Card Component funnel – Step 3: render the Card Component."""

    session["integration_type"] = "Card Component"
    checkout_context = build_checkout_context()
    return render_template("pages/card_component.html", **asdict(checkout_context))


@bp.route("/dropin/checkout")
@register_integration(
    name="Drop-in",
    description="Pre-built UI with all available payment methods in your MA.",
    order=1,
)
@require_session
def dropin_checkout() -> str | Response:
    """Drop-in funnel – Step 3: render the Drop-in payment form."""

    session["integration_type"] = "Drop-in"
    checkout_context = build_checkout_context()
    return render_template("pages/dropin.html", **asdict(checkout_context))


@bp.route("/sessions/dropin/checkout")
@register_integration(
    name="Drop-in",
    description="Pre-built UI powered by /sessions \u2014 Adyen handles the full payment flow.",
    order=3,
    category="Sessions",
)
@require_session
def sessions_dropin_checkout() -> str | Response:
    """Sessions Drop-in funnel \u2013 Step 3: render the Drop-in using /sessions."""

    session["integration_type"] = "Drop-in (Sessions)"
    checkout_context = build_checkout_context()
    return render_template("pages/sessions_dropin.html", **asdict(checkout_context))


@bp.route("/sessions/components/checkout")
@register_integration(
    name="Components",
    description="Card fields only, powered by /sessions \u2014 you control the UI, Adyen handles the flow.",
    note="(Only Card Component implemented for now)",
    order=4,
    category="Sessions",
)
@require_session
def sessions_components_checkout() -> str | Response:
    """Sessions Card Component funnel \u2013 Step 3: render the Card Component using /sessions."""

    session["integration_type"] = "Card Component (Sessions)"
    checkout_context = build_checkout_context()
    return render_template("pages/sessions_card_component.html", **asdict(checkout_context))


@bp.route("/result")
def result() -> str | Response:
    """Render the payment result page and clear the session."""
    raw_result = session.pop("payment_result", None)
    if not raw_result:
        return redirect(url_for("pages.index"))

    payment_result = PaymentResult(**raw_result)
    integration_type = session.get("integration_type", "Unknown")
    session.clear()

    return render_template(
        "pages/result.html",
        payment_result=payment_result,
        integration_type=integration_type,
    )
