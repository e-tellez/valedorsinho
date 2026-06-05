"""Merchant vertical definitions and their suggested /payments payloads.

Each vertical has:
- key: unique identifier
- label: display name
- description: short explanation shown in the UI
- payload: recommended /payments request body (placeholder for now)

Replace the placeholder payloads with real ones when available.
"""

from __future__ import annotations

from typing import Any

VERTICALS: list[dict[str, Any]] = [
    {
        "key": "retail",
        "label": "Retail",
        "description": "Standard e-commerce retail transactions.",
        "payload": {
            "merchantAccount": "YOUR_MERCHANT_ACCOUNT",
            "reference": "retail-order-001",
            "amount": {"value": 5000, "currency": "EUR"},
            "paymentMethod": {"type": "scheme"},
            "returnUrl": "https://your-domain.com/redirect",
            "channel": "Web",
            "countryCode": "NL",
            "shopperLocale": "en-US",
        },
    },
    {
        "key": "food_and_beverage",
        "label": "Food & Beverage",
        "description": "Restaurants, cafes, and quick-service merchants.",
        "payload": {
            "merchantAccount": "YOUR_MERCHANT_ACCOUNT",
            "reference": "fnb-order-001",
            "amount": {"value": 1500, "currency": "EUR"},
            "paymentMethod": {"type": "scheme"},
            "returnUrl": "https://your-domain.com/redirect",
            "channel": "Web",
            "countryCode": "NL",
        },
    },
    {
        "key": "hospitality",
        "label": "Hospitality",
        "description": "Hotels, resorts, and travel bookings.",
        "payload": {
            "merchantAccount": "YOUR_MERCHANT_ACCOUNT",
            "reference": "hotel-booking-001",
            "amount": {"value": 25000, "currency": "EUR"},
            "paymentMethod": {"type": "scheme"},
            "returnUrl": "https://your-domain.com/redirect",
            "channel": "Web",
            "countryCode": "NL",
        },
    },
    {
        "key": "digital_goods",
        "label": "Digital Goods",
        "description": "Software, subscriptions, and digital content.",
        "payload": {
            "merchantAccount": "YOUR_MERCHANT_ACCOUNT",
            "reference": "digital-order-001",
            "amount": {"value": 999, "currency": "USD"},
            "paymentMethod": {"type": "scheme"},
            "returnUrl": "https://your-domain.com/redirect",
            "channel": "Web",
            "countryCode": "US",
        },
    },
    {
        "key": "mobility",
        "label": "Mobility",
        "description": "Ride-hailing, car rentals, and transportation.",
        "payload": {
            "merchantAccount": "YOUR_MERCHANT_ACCOUNT",
            "reference": "mobility-order-001",
            "amount": {"value": 3500, "currency": "EUR"},
            "paymentMethod": {"type": "scheme"},
            "returnUrl": "https://your-domain.com/redirect",
            "channel": "Web",
            "countryCode": "NL",
        },
    },
    {
        "key": "platforms",
        "label": "Platforms / Marketplaces",
        "description": "Multi-seller platforms and marketplace payments.",
        "payload": {
            "merchantAccount": "YOUR_MERCHANT_ACCOUNT",
            "reference": "platform-order-001",
            "amount": {"value": 10000, "currency": "EUR"},
            "paymentMethod": {"type": "scheme"},
            "returnUrl": "https://your-domain.com/redirect",
            "channel": "Web",
            "countryCode": "NL",
        },
    },
]
