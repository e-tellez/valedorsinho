"""Supabase adapter — implements AuthGateway via Supabase REST API and JWT verification."""

from __future__ import annotations

import logging
from typing import Any

import jwt
import requests as http_requests

from app.domain.models.auth import (
    AdyenAccount,
    AdyenCredentials,
    ManagedUser,
    UserProfile,
    UserRole,
)
from app.ports.auth_port import AuthGateway

logger = logging.getLogger(__name__)


class SupabaseAdapter(AuthGateway):
    """Concrete adapter that verifies Supabase JWTs and reads/writes Supabase tables."""

    def __init__(
        self,
        supabase_url: str,
        service_role_key: str,
        jwt_secret: str,
        environment: str,
    ) -> None:
        self._base_url = supabase_url.rstrip("/")
        self._service_role_key = service_role_key
        self._jwt_secret = jwt_secret
        self._environment = environment
        self._headers = {
            "apikey": service_role_key,
            "Authorization": f"Bearer {service_role_key}",
            "Content-Type": "application/json",
        }
        self._jwks_client = jwt.PyJWKClient(
            f"{self._base_url}/auth/v1/.well-known/jwks.json",
            cache_keys=True,
        )

    # ------------------------------------------------------------------
    # AuthGateway — identity
    # ------------------------------------------------------------------

    def verify_token(self, token: str) -> UserProfile:
        """Decode the Supabase JWT, then enrich the profile with the custom role."""
        try:
            header = jwt.get_unverified_header(token)
        except jwt.DecodeError as error:
            raise ValueError(f"Malformed token: {error}")

        algorithm: str = header.get("alg", "HS256")
        logger.debug("JWT algorithm from header: %s", algorithm)

        try:
            if algorithm == "HS256":
                payload: dict[str, Any] = jwt.decode(
                    token,
                    self._jwt_secret,
                    algorithms=["HS256"],
                    audience="authenticated",
                )
            else:
                signing_key = self._jwks_client.get_signing_key_from_jwt(token)
                payload = jwt.decode(
                    token,
                    signing_key.key,
                    algorithms=[algorithm],
                    audience="authenticated",
                )
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError as error:
            raise ValueError(f"Invalid token: {error}")

        user_id: str = payload["sub"]
        email: str = payload.get("email", "")
        role = self._fetch_role(user_id)
        return UserProfile(user_id=user_id, email=email, role=role)

    # ------------------------------------------------------------------
    # AuthGateway — active Adyen credentials
    # ------------------------------------------------------------------

    def get_adyen_config(self, user_id: str) -> AdyenCredentials | None:
        """Return the active account's credentials, or None if unset/empty."""
        active_id = self._get_active_config_id(user_id)
        if not active_id:
            return None
        row = self._get_config_row(user_id, active_id)
        if row is None or not row.get("api_key"):
            return None
        return AdyenCredentials(
            api_key=row["api_key"],
            client_key=row["client_key"],
            merchant_account=row["merchant_account"],
            environment=self._environment,
            locked=row.get("locked", False),
        )

    def upsert_adyen_config(self, user_id: str, credentials: AdyenCredentials) -> AdyenCredentials:
        """Create or update the *active* account row (legacy single-config path)."""
        active_id = self._get_active_config_id(user_id)
        if active_id is not None:
            existing = self._get_config_row(user_id, active_id)
            if existing is not None and existing.get("locked"):
                raise PermissionError("This configuration is locked and cannot be modified")
            response = http_requests.patch(
                f"{self._base_url}/rest/v1/adyen_configs",
                headers={**self._headers, "Prefer": "return=representation"},
                params={"id": f"eq.{active_id}", "user_id": f"eq.{user_id}"},
                json={
                    "api_key": credentials.api_key,
                    "client_key": credentials.client_key,
                    "merchant_account": credentials.merchant_account,
                },
                timeout=10,
            )
            self._raise_if_locked(response)
            response.raise_for_status()
            row = response.json()[0]
        else:
            response = http_requests.post(
                f"{self._base_url}/rest/v1/adyen_configs",
                headers={**self._headers, "Prefer": "return=representation"},
                json={
                    "user_id": user_id,
                    "label": "",
                    "api_key": credentials.api_key,
                    "client_key": credentials.client_key,
                    "merchant_account": credentials.merchant_account,
                },
                timeout=10,
            )
            response.raise_for_status()
            row = response.json()[0]
            self._set_active_pointer(user_id, row["id"])

        return AdyenCredentials(
            api_key=row["api_key"],
            client_key=row["client_key"],
            merchant_account=row["merchant_account"],
            environment=self._environment,
            locked=row.get("locked", False),
        )

    # ------------------------------------------------------------------
    # AuthGateway — multiple saved company accounts
    # ------------------------------------------------------------------

    def list_adyen_configs(self, user_id: str) -> list[AdyenAccount]:
        active_id = self._get_active_config_id(user_id)
        response = http_requests.get(
            f"{self._base_url}/rest/v1/adyen_configs",
            headers=self._headers,
            params={
                "user_id": f"eq.{user_id}",
                "select": "id,label,client_key,merchant_account,locked,api_key",
                "order": "created_at.asc",
            },
            timeout=10,
        )
        response.raise_for_status()
        rows: list[dict[str, Any]] = response.json()
        return [self._row_to_account(row, is_active=row["id"] == active_id) for row in rows]

    def create_adyen_config(
        self, user_id: str, label: str, credentials: AdyenCredentials
    ) -> AdyenAccount:
        response = http_requests.post(
            f"{self._base_url}/rest/v1/adyen_configs",
            headers={**self._headers, "Prefer": "return=representation"},
            json={
                "user_id": user_id,
                "label": label,
                "api_key": credentials.api_key,
                "client_key": credentials.client_key,
                "merchant_account": credentials.merchant_account,
            },
            timeout=10,
        )
        response.raise_for_status()
        row = response.json()[0]

        # First account for this user becomes the active one.
        is_active = False
        if self._get_active_config_id(user_id) is None:
            self._set_active_pointer(user_id, row["id"])
            is_active = True
        return self._row_to_account(row, is_active=is_active)

    def update_adyen_config(
        self,
        user_id: str,
        config_id: str,
        label: str,
        api_key: str | None,
        client_key: str,
        merchant_account: str,
    ) -> AdyenAccount:
        existing = self._get_config_row(user_id, config_id)
        if existing is None:
            raise KeyError("Account not found")
        if existing.get("locked"):
            raise PermissionError("This configuration is locked and cannot be modified")

        resolved_api_key = api_key.strip() if api_key and api_key.strip() else existing.get("api_key", "")
        response = http_requests.patch(
            f"{self._base_url}/rest/v1/adyen_configs",
            headers={**self._headers, "Prefer": "return=representation"},
            params={"id": f"eq.{config_id}", "user_id": f"eq.{user_id}"},
            json={
                "label": label,
                "api_key": resolved_api_key,
                "client_key": client_key,
                "merchant_account": merchant_account,
            },
            timeout=10,
        )
        self._raise_if_locked(response)
        response.raise_for_status()
        row = response.json()[0]
        active_id = self._get_active_config_id(user_id)
        return self._row_to_account(row, is_active=row["id"] == active_id)

    def delete_adyen_config(self, user_id: str, config_id: str) -> None:
        existing = self._get_config_row(user_id, config_id)
        if existing is None:
            raise KeyError("Account not found")
        if existing.get("locked"):
            raise PermissionError("This configuration is locked and cannot be deleted")
        response = http_requests.delete(
            f"{self._base_url}/rest/v1/adyen_configs",
            headers=self._headers,
            params={"id": f"eq.{config_id}", "user_id": f"eq.{user_id}"},
            timeout=10,
        )
        response.raise_for_status()

    def set_active_adyen_config(self, user_id: str, config_id: str) -> AdyenAccount:
        existing = self._get_config_row(user_id, config_id)
        if existing is None:
            raise KeyError("Account not found")
        self._set_active_pointer(user_id, config_id)
        return self._row_to_account(existing, is_active=True)

    # ------------------------------------------------------------------
    # AuthGateway — user & role administration
    # ------------------------------------------------------------------

    def list_users(self) -> list[ManagedUser]:
        roles = self._fetch_all_roles()
        users: list[ManagedUser] = []
        page = 1
        per_page = 50
        while True:
            response = http_requests.get(
                f"{self._base_url}/auth/v1/admin/users",
                headers=self._headers,
                params={"page": str(page), "per_page": str(per_page)},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            batch = data.get("users", []) if isinstance(data, dict) else data
            for entry in batch:
                users.append(
                    ManagedUser(
                        user_id=entry["id"],
                        email=entry.get("email", ""),
                        role=roles.get(entry["id"], UserRole.USER),
                    )
                )
            if len(batch) < per_page:
                break
            page += 1
        return users

    def update_user_role(self, user_id: str, role: UserRole) -> ManagedUser:
        response = http_requests.patch(
            f"{self._base_url}/rest/v1/profiles",
            headers={**self._headers, "Prefer": "return=representation"},
            params={"id": f"eq.{user_id}"},
            json={"role": role.value},
            timeout=10,
        )
        response.raise_for_status()
        email = self._fetch_user_email(user_id)
        return ManagedUser(user_id=user_id, email=email, role=role)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _fetch_role(self, user_id: str) -> UserRole:
        response = http_requests.get(
            f"{self._base_url}/rest/v1/profiles",
            headers=self._headers,
            params={"id": f"eq.{user_id}", "select": "role"},
            timeout=10,
        )
        response.raise_for_status()
        rows: list[dict[str, Any]] = response.json()
        if not rows:
            return UserRole.USER
        return self._parse_role(rows[0].get("role", "user"))

    def _fetch_all_roles(self) -> dict[str, UserRole]:
        response = http_requests.get(
            f"{self._base_url}/rest/v1/profiles",
            headers=self._headers,
            params={"select": "id,role"},
            timeout=10,
        )
        response.raise_for_status()
        rows: list[dict[str, Any]] = response.json()
        return {row["id"]: self._parse_role(row.get("role", "user")) for row in rows}

    def _fetch_user_email(self, user_id: str) -> str:
        response = http_requests.get(
            f"{self._base_url}/auth/v1/admin/users/{user_id}",
            headers=self._headers,
            timeout=10,
        )
        response.raise_for_status()
        return response.json().get("email", "")

    def _get_active_config_id(self, user_id: str) -> str | None:
        response = http_requests.get(
            f"{self._base_url}/rest/v1/profiles",
            headers=self._headers,
            params={"id": f"eq.{user_id}", "select": "active_adyen_config_id"},
            timeout=10,
        )
        response.raise_for_status()
        rows: list[dict[str, Any]] = response.json()
        if not rows:
            return None
        return rows[0].get("active_adyen_config_id")

    def _set_active_pointer(self, user_id: str, config_id: str) -> None:
        response = http_requests.patch(
            f"{self._base_url}/rest/v1/profiles",
            headers=self._headers,
            params={"id": f"eq.{user_id}"},
            json={"active_adyen_config_id": config_id},
            timeout=10,
        )
        response.raise_for_status()

    def _get_config_row(self, user_id: str, config_id: str) -> dict[str, Any] | None:
        """Fetch a single account row, enforcing ownership via the user_id filter."""
        response = http_requests.get(
            f"{self._base_url}/rest/v1/adyen_configs",
            headers=self._headers,
            params={
                "id": f"eq.{config_id}",
                "user_id": f"eq.{user_id}",
                "select": "id,label,client_key,merchant_account,locked,api_key",
            },
            timeout=10,
        )
        response.raise_for_status()
        rows: list[dict[str, Any]] = response.json()
        return rows[0] if rows else None

    def _row_to_account(self, row: dict[str, Any], is_active: bool) -> AdyenAccount:
        return AdyenAccount(
            id=row["id"],
            label=row.get("label") or "",
            client_key=row.get("client_key", ""),
            merchant_account=row.get("merchant_account", ""),
            is_active=is_active,
            locked=row.get("locked", False),
            api_key_configured=bool(row.get("api_key")),
        )

    @staticmethod
    def _parse_role(raw_role: str) -> UserRole:
        try:
            return UserRole(raw_role)
        except ValueError:
            return UserRole.USER

    @staticmethod
    def _raise_if_locked(response: http_requests.Response) -> None:
        if response.status_code in (400, 401, 403) and "locked" in response.text.lower():
            raise PermissionError("This configuration is locked and cannot be modified")
