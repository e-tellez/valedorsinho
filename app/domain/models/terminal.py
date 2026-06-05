"""Terminal domain models — decoded response structures and summary fields."""

from __future__ import annotations

from dataclasses import dataclass, field


TERMINAL_API_URLS: dict[str, str] = {
    "test": "https://terminal-api-test.adyen.com/sync",
    "live": "https://terminal-api-live.adyen.com/sync",
}


@dataclass(frozen=True)
class PaymentSummaryField:
    """A single key-value pair in a payment summary."""

    label: str
    value: str


@dataclass
class DecodedTerminalResponse:
    """Result of decoding and analysing a terminal payment response."""

    success: bool = False
    result_title: str = "Payment Failed"
    result_message: str = ""
    decoded_additional_response: dict | str | None = None
    payment_summary: list[PaymentSummaryField] = field(default_factory=list)
