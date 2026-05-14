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
