from app.domain.models.auth import AdyenCredentials, UserProfile, UserRole
from app.ports.auth_port import AuthGateway
from app.use_cases.auth_service import AuthService


class FakeAuthGateway(AuthGateway):
    def __init__(self, credentials: AdyenCredentials | None) -> None:
        self.credentials = credentials

    def verify_token(self, token: str) -> UserProfile:
        raise NotImplementedError

    def get_adyen_config(self, user_id: str) -> AdyenCredentials | None:
        return self.credentials

    def upsert_adyen_config(
        self, user_id: str, credentials: AdyenCredentials
    ) -> AdyenCredentials:
        self.credentials = credentials
        return credentials


def test_update_user_config_preserves_write_only_api_key() -> None:
    gateway = FakeAuthGateway(
        AdyenCredentials(
            api_key="AQE-existing-secret",
            client_key="test_old",
            merchant_account="OldMerchant",
            environment="test",
        )
    )
    service = AuthService(
        auth_gateway=gateway,
        default_credentials=AdyenCredentials("default", "test_default", "Default", "test"),
    )
    user = UserProfile("user-1", "admin@adyen.com", UserRole.ADMIN)

    saved = service.update_user_config(
        user=user,
        api_key=None,
        client_key=" test_new ",
        merchant_account=" NewMerchant ",
    )

    assert saved.api_key == "AQE-existing-secret"
    assert saved.client_key == "test_new"
    assert saved.merchant_account == "NewMerchant"
