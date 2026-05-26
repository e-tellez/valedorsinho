import functools
import uuid

from flask import session, redirect, url_for


def require_session(view_func):
    """Redirect to step 1 if the shopper has not completed the order form."""
    @functools.wraps(view_func)
    def wrapped(*args, **kwargs):
        if session.get("amount_minor_units") is None:
            return redirect(url_for("pages.index"))
        return view_func(*args, **kwargs)
    return wrapped


COUNTRY_CURRENCY_MAP: dict[str, str] = {
    "MX": "MXN",
    "US": "USD",
    "BR": "BRL",
}


def generate_reference() -> str:
    """Return a unique order reference so every payment can be identified."""
    return "order-" + str(uuid.uuid4())


def build_checkout_context():
    """Build a CheckoutContext from the current Flask session and app config.

    Centralises the 8-field template context that every checkout payment page
    (Drop-in, Card Component, and their Sessions variants) needs.
    """
    from checkout.config import CLIENT_KEY, ADYEN_ENVIRONMENT
    from checkout.models import CheckoutContext

    amount_minor_units = session.get("amount_minor_units", 1000)
    return CheckoutContext(
        client_key=CLIENT_KEY,
        environment=ADYEN_ENVIRONMENT,
        shopper_reference=session.get("shopper_reference", ""),
        is_guest=session.get("is_guest", False),
        amount_minor_units=amount_minor_units,
        amount=amount_minor_units / 100,
        country_code=session.get("country_code", "MX"),
        currency=session.get("currency", "MXN"),
    )
