import pytest

from app.ports.validator_port import PayloadValidator
from app.use_cases.tools_service import ToolsService


class FakeValidator(PayloadValidator):
    def validate(self, payload: dict) -> list[dict]:
        return []


def test_suggested_payload_deep_merges_selected_verticals() -> None:
    service = ToolsService(
        FakeValidator(),
        [
            {"key": "first", "payload": {"additionalData": {"a": 1}, "channel": "Web"}},
            {"key": "second", "payload": {"additionalData": {"b": 2}}},
        ],
    )

    result = service.get_suggested_payload(["first", "second"])

    assert result["payload"]["additionalData"] == {"a": 1, "b": 2}
    assert result["payload"]["channel"] == "Web"


def test_suggested_payload_rejects_unknown_verticals() -> None:
    service = ToolsService(FakeValidator(), [])

    with pytest.raises(ValueError, match="Unknown vertical keys: missing"):
        service.get_suggested_payload(["missing"])
