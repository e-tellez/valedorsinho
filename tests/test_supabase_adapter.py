from typing import Any

from app.adapters.supabase_adapter import SupabaseAdapter
from app.domain.models.auth import AdyenCredentials


class FakeResponse:
    status_code = 200
    text = ""

    def raise_for_status(self) -> None:
        return None

    def json(self) -> list[dict[str, Any]]:
        return [
            {
                "api_key": "AQE-secret",
                "client_key": "test_client",
                "merchant_account": "MerchantECOM",
                "locked": False,
            }
        ]


def test_upsert_uses_user_id_as_conflict_target(monkeypatch) -> None:
    adapter = SupabaseAdapter("https://example.supabase.co", "service-role", "secret", "test")
    monkeypatch.setattr(adapter, "get_adyen_config", lambda user_id: None)
    captured: dict[str, Any] = {}

    def fake_post(*args, **kwargs) -> FakeResponse:
        captured.update(kwargs)
        return FakeResponse()

    monkeypatch.setattr("app.adapters.supabase_adapter.http_requests.post", fake_post)

    adapter.upsert_adyen_config(
        "user-1",
        AdyenCredentials("AQE-secret", "test_client", "MerchantECOM", "test"),
    )

    assert captured["params"] == {"on_conflict": "user_id"}
