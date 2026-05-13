import uuid

COUNTRY_CURRENCY_MAP = {
    "MX": ("MX", "MXN"),
    "US": ("US", "USD"),
    "BR": ("BR", "BRL"),
}


def generate_reference():
    """Return a unique order reference so every payment can be identified."""
    return "order-" + str(uuid.uuid4())
