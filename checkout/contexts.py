"""Template context objects.

These replace loose kwargs in render_template() calls, keeping each
route handler short and making the expected template variables explicit.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CheckoutContext:
    """Template context shared by all checkout payment pages (Drop-in, Card
    Component, and their Sessions variants)."""

    client_key: str
    environment: str
    shopper_reference: str
    is_guest: bool
    amount_minor_units: int
    amount: float
    country_code: str
    currency: str


@dataclass(frozen=True)
class OrderFormContext:
    """Template context for the order form page."""

    form_action: str
    is_guest: bool
    username: str
    amount: str
    country: str
    error: str | None = None
    amount_error: str | None = None
    amount_warning: str | None = None


@dataclass(frozen=True)
class PaymentResult:
    """Outcome of a payment, stored in the Flask session between routes."""

    status: str
    result_code: str
    adyen_response: dict[str, Any] | None = None
