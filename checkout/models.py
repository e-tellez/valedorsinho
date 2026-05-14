"""Data models for Adyen API requests.

Each model maps Python-style attributes to the camelCase keys expected by the
Adyen Checkout API.  Using dataclasses gives us type safety, IDE autocompletion,
and a single place to see every field a request can carry.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Shared value objects
# ---------------------------------------------------------------------------

@dataclass
class Amount:
    """Monetary amount in minor units (e.g. 1000 = $10.00)."""

    value: int
    currency: str

    def to_dict(self) -> dict[str, Any]:
        return {"value": self.value, "currency": self.currency}


@dataclass
class BillingAddress:
    """Billing address sent with a payment request."""

    street: str = "Teststreet 1"
    house_number_or_name: str = "1"
    postal_code: str = "12345"
    city: str = "Amsterdam"
    state_or_province: str = "NH"
    country: str = "NL"

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> BillingAddress:
        """Build a BillingAddress from a camelCase dict (e.g. from the browser)."""
        return cls(
            street=data.get("street", cls.street),
            house_number_or_name=data.get("houseNumberOrName", cls.house_number_or_name),
            postal_code=data.get("postalCode", cls.postal_code),
            city=data.get("city", cls.city),
            state_or_province=data.get("stateOrProvince", cls.state_or_province),
            country=data.get("country", cls.country),
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "street": self.street,
            "houseNumberOrName": self.house_number_or_name,
            "postalCode": self.postal_code,
            "city": self.city,
            "stateOrProvince": self.state_or_province,
            "country": self.country,
        }


# ---------------------------------------------------------------------------
# /paymentMethods request
# ---------------------------------------------------------------------------

@dataclass
class PaymentMethodsRequest:
    """Body for POST /paymentMethods."""

    merchant_account: str
    amount: Amount
    country_code: str
    shopper_reference: str = ""
    shopper_locale: str = "en-US"
    channel: str = "Web"

    def to_dict(self) -> dict[str, Any]:
        return {
            "merchantAccount": self.merchant_account,
            "amount": self.amount.to_dict(),
            "countryCode": self.country_code,
            "shopperLocale": self.shopper_locale,
            "channel": self.channel,
            "shopperReference": self.shopper_reference,
        }


# ---------------------------------------------------------------------------
# /payments request
# ---------------------------------------------------------------------------

@dataclass
class PaymentRequest:
    """Body for POST /payments."""

    merchant_account: str
    reference: str
    amount: Amount
    country_code: str
    payment_method: dict[str, Any]
    return_url: str
    origin: str
    shopper_reference: str
    shopper_ip: str
    shopper_email: str = "shopper@example.com"
    browser_info: dict[str, Any] | None = None
    billing_address: BillingAddress = field(default_factory=BillingAddress)
    store_payment_method: bool = False
    recurring_processing_model: str = "CardOnFile"
    native_three_ds: str = "preferred"
    channel: str = "Web"

    @property
    def shopper_interaction(self) -> str:
        """Ecommerce for new cards, ContAuth for stored (tokenised) cards."""
        if self.payment_method.get("storedPaymentMethodId"):
            return "ContAuth"
        return "Ecommerce"

    def to_dict(self) -> dict[str, Any]:
        return {
            "merchantAccount": self.merchant_account,
            "reference": self.reference,
            "amount": self.amount.to_dict(),
            "countryCode": self.country_code,
            "paymentMethod": self.payment_method,
            "authenticationData": {
                "threeDSRequestData": {
                    "nativeThreeDS": self.native_three_ds,
                },
            },
            "channel": self.channel,
            "returnUrl": self.return_url,
            "browserInfo": self.browser_info,
            "origin": self.origin,
            "shopperReference": self.shopper_reference,
            "recurringProcessingModel": self.recurring_processing_model,
            "storePaymentMethod": self.store_payment_method,
            "shopperInteraction": self.shopper_interaction,
            "shopperIP": self.shopper_ip,
            "shopperEmail": self.shopper_email,
            "billingAddress": self.billing_address.to_dict(),
        }


# ---------------------------------------------------------------------------
# /payments/details request
# ---------------------------------------------------------------------------

@dataclass
class PaymentDetailsRequest:
    """Body for POST /payments/details."""

    details: dict[str, Any]
    payment_data: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"details": self.details}
        if self.payment_data:
            result["paymentData"] = self.payment_data
        return result
