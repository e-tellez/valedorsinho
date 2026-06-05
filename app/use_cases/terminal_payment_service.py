"""Terminal payment use cases — orchestrates terminal gateway and response decoding."""

from __future__ import annotations

import logging
from typing import Any

from app.domain.models.terminal import DecodedTerminalResponse, PaymentSummaryField
from app.ports.management_port import ManagementGateway
from app.ports.terminal_port import TerminalGateway

logger = logging.getLogger(__name__)


class TerminalPaymentService:
    """Application service for terminal payment operations."""

    def __init__(
        self,
        terminal_gateway: TerminalGateway,
        management_gateway: ManagementGateway,
        decode_additional_response_fn,
        extract_payment_summary_fn,
    ) -> None:
        self._terminal_gateway = terminal_gateway
        self._management_gateway = management_gateway
        self._decode_additional_response = decode_additional_response_fn
        self._extract_payment_summary = extract_payment_summary_fn

    def list_merchants(self, query_params: dict[str, str]) -> dict[str, Any]:
        return self._management_gateway.list_merchant_accounts(query_params)

    def list_stores(self, merchant_id: str, query_params: dict[str, str]) -> dict[str, Any]:
        return self._management_gateway.list_stores(merchant_id, query_params)

    def list_terminals(self, query_params: dict[str, str]) -> dict[str, Any]:
        return self._management_gateway.list_terminals(query_params)

    def make_payment(self, sale_to_poi_request: dict[str, Any]) -> dict[str, Any]:
        return self._terminal_gateway.send_payment(sale_to_poi_request)

    def decode_response(self, response_data: dict[str, Any]) -> DecodedTerminalResponse:
        """Decode a SaleToPOIResponse and extract payment summary."""
        result = DecodedTerminalResponse()

        sal_response = response_data.get("SaleToPOIResponse", {}) if isinstance(response_data, dict) else {}
        poi_response = sal_response.get("PaymentResponse", {})

        if poi_response:
            response_block = poi_response.get("Response", {})
            result_text = response_block.get("Result", "")
            error_condition = response_block.get("ErrorCondition", "")
            result.success = result_text == "Success"
            result.result_title = "Payment Approved" if result.success else "Payment Declined"

            if not result.success and error_condition:
                result.result_message = f"ErrorCondition: {error_condition}"

            additional = response_block.get("AdditionalResponse", "")
            result.decoded_additional_response = self._decode_additional_response(additional)

            raw_summary = self._extract_payment_summary(result.decoded_additional_response, poi_response)
            result.payment_summary = [
                PaymentSummaryField(label=label, value=value)
                for label, value in raw_summary
            ]
        elif "error" in response_data:
            result.result_title = "Error"
            result.result_message = response_data.get("error", "")

        return result
