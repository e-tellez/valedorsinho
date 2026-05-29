"""Shared helper utilities."""

import uuid


COUNTRY_CURRENCY_MAP: dict[str, str] = {
    "MX": "MXN",
    "US": "USD",
    "BR": "BRL",
}


def generate_reference() -> str:
    """Return a unique order reference so every payment can be identified."""
    return "order-" + str(uuid.uuid4())
