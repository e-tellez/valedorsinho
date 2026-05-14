"""Data models for Adyen API requests.

Each model maps Python-style attributes to the camelCase keys expected by the
Adyen Checkout API.  Using Pydantic gives us automatic validation, camelCase
serialisation via aliases, and a single place to see every field a request can
carry — with zero manual to_dict() boilerplate.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, computed_field
from pydantic.alias_generators import to_camel


class AdyenModel(BaseModel):
    """Base for all Adyen request models.

    - Accepts snake_case on init, serialises to camelCase via aliases.
    - populate_by_name lets callers use either style.
    """

    model_config = {
        "alias_generator": to_camel,
        "populate_by_name": True,
    }


# ---------------------------------------------------------------------------
# Shared value objects
# ---------------------------------------------------------------------------

class Amount(AdyenModel):
    """Monetary amount in minor units (e.g. 1000 = $10.00)."""

    value: int
    currency: str


class BillingAddress(AdyenModel):
    """Billing address sent with a payment request."""

    street: str = "Teststreet 1"
    house_number_or_name: str = "1"
    postal_code: str = "12345"
    city: str = "Amsterdam"
    state_or_province: str = "NH"
    country: str = "NL"


class ThreeDSRequestData(AdyenModel):
    """3DS configuration nested inside authenticationData."""

    native_three_ds: str = Field(default="preferred", alias="nativeThreeDS")


class AuthenticationData(AdyenModel):
    """Wrapper for 3DS request configuration."""

    three_ds_request_data: ThreeDSRequestData = Field(
        default_factory=ThreeDSRequestData,
        alias="threeDSRequestData",
    )


# ---------------------------------------------------------------------------
# /paymentMethods request
# ---------------------------------------------------------------------------

class PaymentMethodsRequest(AdyenModel):
    """Body for POST /paymentMethods."""

    merchant_account: str
    amount: Amount
    country_code: str
    shopper_reference: str = ""
    shopper_locale: str = "en-US"
    channel: str = "Web"


# ---------------------------------------------------------------------------
# /payments request
# ---------------------------------------------------------------------------

class PaymentRequest(AdyenModel):
    """Body for POST /payments."""

    merchant_account: str
    reference: str
    amount: Amount
    country_code: str
    payment_method: dict[str, Any]
    return_url: str
    origin: str
    shopper_reference: str
    shopper_ip: str = Field(alias="shopperIP")
    shopper_email: str = "shopper@example.com"
    browser_info: dict[str, Any] | None = None
    billing_address: BillingAddress = Field(default_factory=BillingAddress)
    store_payment_method: bool = False
    recurring_processing_model: str = "CardOnFile"
    authentication_data: AuthenticationData = Field(default_factory=AuthenticationData)
    channel: str = "Web"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def shopper_interaction(self) -> str:
        """Ecommerce for new cards, ContAuth for stored (tokenised) cards."""
        if self.payment_method.get("storedPaymentMethodId"):
            return "ContAuth"
        return "Ecommerce"


# ---------------------------------------------------------------------------
# /payments/details request
# ---------------------------------------------------------------------------

class PaymentDetailsRequest(AdyenModel):
    """Body for POST /payments/details."""

    details: dict[str, Any]
    payment_data: str | None = None
