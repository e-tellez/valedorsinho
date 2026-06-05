"""Checkout use cases — orchestrates domain models and the checkout gateway."""

from __future__ import annotations

import logging
import uuid
from typing import Any

from app.domain.models.checkout import (
    Amount,
    BillingAddress,
    PaymentDetailsRequest,
    PaymentMethodsRequest,
    PaymentRequest,
    SessionsRequest,
)
from app.ports.checkout_port import CheckoutGateway

logger = logging.getLogger(__name__)

COUNTRY_CURRENCY_MAP: dict[str, str] = {
    "MX": "MXN",
    "US": "USD",
    "BR": "BRL",
}


def _generate_reference() -> str:
    return "order-" + str(uuid.uuid4())


class CheckoutService:
    """Application service that encapsulates all checkout use cases."""

    def __init__(self, gateway: CheckoutGateway, merchant_account: str) -> None:
        self._gateway = gateway
        self._merchant_account = merchant_account

    # ----- /paymentMethods -----

    def get_payment_methods(
        self,
        amount_value: int,
        currency: str,
        country_code: str,
        shopper_locale: str,
        shopper_reference: str | None,
    ) -> dict[str, Any]:
        request_model = PaymentMethodsRequest(
            merchant_account=self._merchant_account,
            amount=Amount(value=amount_value, currency=currency),
            country_code=country_code,
            shopper_locale=shopper_locale,
            shopper_reference=shopper_reference,
        )
        request_body = request_model.model_dump(by_alias=True, exclude_none=True)
        response = self._gateway.get_payment_methods(request_body)
        return {"requestBody": request_body, "response": response}

    # ----- /payments -----

    def create_payment(
        self,
        payment_method: dict[str, Any],
        amount_value: int,
        currency: str,
        country_code: str,
        return_url: str,
        origin: str,
        shopper_ip: str,
        shopper_reference: str | None = None,
        is_guest: bool = False,
        shopper_email: str = "shopper@example.com",
        browser_info: dict[str, Any] | None = None,
        billing_address: dict[str, Any] | None = None,
        store_payment_method: bool = False,
    ) -> dict[str, Any]:
        order_ref = _generate_reference()
        payment_request = PaymentRequest(
            merchant_account=self._merchant_account,
            reference=order_ref,
            amount=Amount(value=amount_value, currency=currency),
            country_code=country_code,
            payment_method=payment_method,
            return_url=return_url,
            origin=origin,
            shopper_reference=shopper_reference,
            shopper_ip=shopper_ip,
            shopper_email=shopper_email,
            browser_info=browser_info,
            billing_address=BillingAddress(**billing_address) if billing_address else BillingAddress(),
            store_payment_method=store_payment_method if not is_guest else None,
            recurring_processing_model="CardOnFile" if not is_guest and shopper_reference else None,
        )
        return self._gateway.make_payment(
            payment_request.model_dump(by_alias=True, exclude_none=True)
        )

    # ----- /payments/details -----

    def submit_payment_details(
        self,
        details: dict[str, Any],
        payment_data: str | None = None,
    ) -> dict[str, Any]:
        details_request = PaymentDetailsRequest(
            details=details,
            payment_data=payment_data,
        )
        return self._gateway.payment_details(
            details_request.model_dump(by_alias=True, exclude_none=True)
        )

    # ----- /sessions -----

    def create_session(
        self,
        amount_value: int,
        currency: str,
        country_code: str,
        return_url: str,
        shopper_reference: str | None = None,
        is_guest: bool = False,
        shopper_email: str = "shopper@example.com",
    ) -> dict[str, Any]:
        order_ref = _generate_reference()
        sessions_request = SessionsRequest(
            merchant_account=self._merchant_account,
            reference=order_ref,
            amount=Amount(value=amount_value, currency=currency),
            country_code=country_code,
            return_url=return_url,
            shopper_reference=shopper_reference,
            shopper_email=shopper_email,
            store_payment_method_mode=(
                "askForConsent" if not is_guest and shopper_reference else None
            ),
            recurring_processing_model=(
                "CardOnFile" if not is_guest and shopper_reference else None
            ),
        )
        request_body = sessions_request.model_dump(by_alias=True, exclude_none=True)
        response = self._gateway.create_session(request_body)
        return {"requestBody": request_body, "response": response}

    # ----- disable stored method -----

    def disable_stored_method(
        self,
        shopper_reference: str,
        stored_payment_method_id: str,
    ) -> dict[str, Any]:
        disable_request = {
            "merchantAccount": self._merchant_account,
            "shopperReference": shopper_reference,
            "recurringDetailReference": stored_payment_method_id,
        }
        return self._gateway.disable_stored_method(disable_request)

    # ----- redirect handler -----

    def handle_redirect(
        self,
        redirect_result: str,
        payment_data: str | None = None,
    ) -> dict[str, Any]:
        details_request = PaymentDetailsRequest(
            details={"redirectResult": redirect_result},
            payment_data=payment_data,
        )
        return self._gateway.payment_details(
            details_request.model_dump(by_alias=True, exclude_none=True)
        )
