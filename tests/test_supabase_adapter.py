from typing import Any

from app.adapters.supabase_adapter import SupabaseAdapter


class FakeResponse:
    def __init__(self, json_data: Any, status_code: int = 200, text: str = "") -> None:
        self._json = json_data
        self.status_code = status_code
        self.text = text

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise AssertionError(f"unexpected HTTP {self.status_code}")

    def json(self) -> Any:
        return self._json


def _adapter() -> SupabaseAdapter:
    return SupabaseAdapter("https://example.supabase.co", "service-role", "secret", "test")


def test_get_adyen_config_resolves_active_pointer(monkeypatch) -> None:
    adapter = _adapter()

    def fake_get(url: str, **kwargs: Any) -> FakeResponse:
        params = kwargs.get("params", {})
        if "/rest/v1/profiles" in url and params.get("select") == "active_adyen_config_id":
            return FakeResponse([{"active_adyen_config_id": "cfg-1"}])
        if "/rest/v1/adyen_configs" in url and params.get("id") == "eq.cfg-1":
            return FakeResponse(
                [{
                    "id": "cfg-1",
                    "label": "Primary",
                    "api_key": "AQE-secret",
                    "client_key": "test_client",
                    "merchant_account": "MerchantECOM",
                    "locked": False,
                }]
            )
        raise AssertionError(f"unexpected GET {url} {params}")

    monkeypatch.setattr("app.adapters.supabase_adapter.http_requests.get", fake_get)

    creds = adapter.get_adyen_config("user-1")
    assert creds is not None
    assert creds.merchant_account == "MerchantECOM"
    assert creds.api_key == "AQE-secret"


def test_get_adyen_config_none_when_no_active_pointer(monkeypatch) -> None:
    adapter = _adapter()
    monkeypatch.setattr(
        "app.adapters.supabase_adapter.http_requests.get",
        lambda url, **kwargs: FakeResponse([{"active_adyen_config_id": None}]),
    )
    assert adapter.get_adyen_config("user-1") is None


def test_list_adyen_configs_marks_active_and_hides_api_key(monkeypatch) -> None:
    adapter = _adapter()

    def fake_get(url: str, **kwargs: Any) -> FakeResponse:
        params = kwargs.get("params", {})
        if "/rest/v1/profiles" in url:
            return FakeResponse([{"active_adyen_config_id": "cfg-1"}])
        if "/rest/v1/adyen_configs" in url:
            assert params.get("user_id") == "eq.user-1"  # ownership filter
            return FakeResponse([
                {"id": "cfg-1", "label": "A", "client_key": "ck1", "merchant_account": "MA1", "locked": False, "api_key": "AQE"},
                {"id": "cfg-2", "label": "B", "client_key": "ck2", "merchant_account": "MA2", "locked": False, "api_key": ""},
            ])
        raise AssertionError(f"unexpected GET {url}")

    monkeypatch.setattr("app.adapters.supabase_adapter.http_requests.get", fake_get)

    accounts = adapter.list_adyen_configs("user-1")
    assert [a.id for a in accounts] == ["cfg-1", "cfg-2"]
    assert accounts[0].is_active is True and accounts[0].api_key_configured is True
    assert accounts[1].is_active is False and accounts[1].api_key_configured is False
    assert not hasattr(accounts[0], "api_key")


def test_set_active_adyen_config_patches_profile_pointer(monkeypatch) -> None:
    adapter = _adapter()
    captured: dict[str, Any] = {}

    def fake_get(url: str, **kwargs: Any) -> FakeResponse:
        # ownership lookup for _get_config_row
        return FakeResponse([
            {"id": "cfg-9", "label": "X", "client_key": "ck", "merchant_account": "MA", "locked": False, "api_key": "AQE"}
        ])

    def fake_patch(url: str, **kwargs: Any) -> FakeResponse:
        captured["url"] = url
        captured["params"] = kwargs.get("params")
        captured["json"] = kwargs.get("json")
        return FakeResponse([])

    monkeypatch.setattr("app.adapters.supabase_adapter.http_requests.get", fake_get)
    monkeypatch.setattr("app.adapters.supabase_adapter.http_requests.patch", fake_patch)

    account = adapter.set_active_adyen_config("user-1", "cfg-9")
    assert account.is_active is True
    assert "/rest/v1/profiles" in captured["url"]
    assert captured["params"] == {"id": "eq.user-1"}
    assert captured["json"] == {"active_adyen_config_id": "cfg-9"}


def test_update_adyen_config_blocks_locked(monkeypatch) -> None:
    adapter = _adapter()
    monkeypatch.setattr(
        "app.adapters.supabase_adapter.http_requests.get",
        lambda url, **kwargs: FakeResponse([
            {"id": "cfg-1", "label": "A", "client_key": "ck", "merchant_account": "MA", "locked": True, "api_key": "AQE"}
        ]),
    )
    try:
        adapter.update_adyen_config("user-1", "cfg-1", "A", None, "ck", "MA")
        raise AssertionError("expected PermissionError")
    except PermissionError:
        pass
