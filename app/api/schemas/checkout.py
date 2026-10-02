"""Request/Response DTOs for checkout endpoints (driving adapter layer)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel


class CreatePaymentBody(BaseModel):
    """Body sent by the frontend to POST /api/checkout/payments."""

    model_config = {"alias_generator": to_camel, "populate_by_name": True}

    payment_method: dict[str, Any]
    amount_value: int
    currency: str = "MXN"
    country_code: str = "MX"
    shopper_reference: str | None = None
    is_guest: bool = False
    shopper_email: str = "shopper@example.com"
    browser_info: dict[str, Any] | None = None
    billing_address: dict[str, Any] | None = None
    store_payment_method: bool = False
    return_url: str
    origin: str


class CreateSessionBody(BaseModel):
    """Body sent by the frontend to POST /api/checkout/sessions."""

    model_config = {"alias_generator": to_camel, "populate_by_name": True}

    amount_value: int
    currency: str = "MXN"
    country_code: str = "MX"
    shopper_reference: str | None = None
    is_guest: bool = False
    shopper_email: str = "shopper@example.com"
    return_url: str


class PaymentDetailsBody(BaseModel):
    """Body sent by the frontend to POST /api/checkout/payments/details."""

    model_config = {"alias_generator": to_camel, "populate_by_name": True}

    details: dict[str, Any]
    payment_data: str | None = None


class DisableStoredMethodBody(BaseModel):
    """Body sent by the frontend to POST /api/checkout/disable."""

    model_config = {"alias_generator": to_camel, "populate_by_name": True}

    shopper_reference: str
    stored_payment_method_id: str


class RedirectBody(BaseModel):
    """Body sent by the frontend to POST /api/checkout/redirect."""

    model_config = {"alias_generator": to_camel, "populate_by_name": True}

    redirect_result: str
    payment_data: str | None = None


class ApplePayPaymentMethodsBody(BaseModel):
    model_config = {"alias_generator": to_camel, "populate_by_name": True}

    country_code: str = "MX"
    currency: str = "MXN"


class ApplePaySessionBody(BaseModel):
    model_config = {"alias_generator": to_camel, "populate_by_name": True}

    merchant_identifier: str = Field(min_length=1)
    display_name: str = Field(min_length=1)


class ApplePayPaymentBody(BaseModel):
    model_config = {"alias_generator": to_camel, "populate_by_name": True}

    apple_pay_token: str = Field(min_length=1)
    amount_value: int = Field(gt=0)
    installment_count: Literal[3, 6, 9, 12]
