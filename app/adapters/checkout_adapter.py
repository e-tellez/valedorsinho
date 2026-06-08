"""Adyen Checkout SDK adapter — implements CheckoutGateway port."""

from __future__ import annotations

import logging
from typing import Any

import Adyen

from app.ports.checkout_port import CheckoutGateway

logger = logging.getLogger(__name__)


class CheckoutAdapter(CheckoutGateway):
    """Concrete adapter that calls the Adyen Python SDK for checkout operations."""

    def __init__(self, client: Adyen.Adyen) -> None:
        self._client = client

    def get_payment_methods(self, request_body: dict[str, Any]) -> dict[str, Any]:
        response = self._client.checkout.payments_api.payment_methods(request_body)
        return response.message

    def make_payment(self, request_body: dict[str, Any]) -> dict[str, Any]:
        response = self._client.checkout.payments_api.payments(request_body)
        return response.message

    def payment_details(self, request_body: dict[str, Any]) -> dict[str, Any]:
        response = self._client.checkout.payments_api.payments_details(request_body)
        return response.message

    def create_session(self, request_body: dict[str, Any]) -> dict[str, Any]:
        response = self._client.checkout.payments_api.sessions(request_body)
        return response.message

    def disable_stored_method(self, request_body: dict[str, Any]) -> dict[str, Any]:
        response = self._client.recurring.recurring_api.disable(request_body)
        return response.message
