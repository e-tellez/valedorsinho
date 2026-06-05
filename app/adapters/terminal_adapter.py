"""Adyen Terminal API Cloud adapter — implements TerminalGateway port."""

from __future__ import annotations

import logging
from typing import Any

import requests as http_requests
from fastapi import HTTPException

from app.domain.models.terminal import TERMINAL_API_URLS
from app.ports.terminal_port import TerminalGateway

logger = logging.getLogger(__name__)


class TerminalAdapter(TerminalGateway):
    """Concrete adapter that calls the Adyen Terminal API (Cloud)."""

    def __init__(self, api_key: str, environment: str) -> None:
        self._api_key = api_key
        self._environment = environment

    def send_payment(self, sale_to_poi_request: dict[str, Any]) -> dict[str, Any]:
        terminal_api_url = TERMINAL_API_URLS.get(self._environment, TERMINAL_API_URLS["test"])

        try:
            terminal_response = http_requests.post(
                terminal_api_url,
                json=sale_to_poi_request,
                headers={
                    "x-API-key": self._api_key,
                    "Content-Type": "application/json",
                },
                timeout=300,
            )
        except http_requests.RequestException as error:
            logger.error("Terminal API request failed: %s", error)
            raise HTTPException(status_code=502, detail=str(error))

        try:
            response_body = terminal_response.json()
        except ValueError:
            logger.error(
                "Invalid JSON in terminal response (HTTP %s): %s",
                terminal_response.status_code, terminal_response.text[:500],
            )
            raise HTTPException(
                status_code=502,
                detail=f"Invalid JSON in terminal response: {terminal_response.text[:500]}",
            )

        sal_resp = response_body.get("SaleToPOIResponse", {}) if isinstance(response_body, dict) else {}
        logger.info(
            "Terminal API response – HTTP %s, SaleToPOIResponse keys: %s, Result: %s",
            terminal_response.status_code,
            list(sal_resp.keys()) if sal_resp else "N/A",
            sal_resp.get("PaymentResponse", {}).get("Response", {}).get("Result", "N/A"),
        )

        if terminal_response.status_code >= 400:
            raise HTTPException(status_code=terminal_response.status_code, detail=response_body)

        return response_body
