"""Supabase adapter — implements AuthGateway via Supabase REST API and JWT verification."""

from __future__ import annotations

import logging
from typing import Any

import jwt
import requests as http_requests

from app.domain.models.auth import AdyenCredentials, UserProfile, UserRole
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
    # AuthGateway
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

    def get_adyen_config(self, user_id: str) -> AdyenCredentials | None:
        response = http_requests.get(
            f"{self._base_url}/rest/v1/adyen_configs",
            headers=self._headers,
            params={
                "user_id": f"eq.{user_id}",
                "select": "api_key,client_key,merchant_account,locked",
            },
            timeout=10,
        )
        response.raise_for_status()
        rows: list[dict[str, Any]] = response.json()
        if not rows or not rows[0].get("api_key"):
            return None
        row = rows[0]
        return AdyenCredentials(
            api_key=row["api_key"],
            client_key=row["client_key"],
            merchant_account=row["merchant_account"],
            environment=self._environment,
            locked=row.get("locked", False),
        )

    def upsert_adyen_config(self, user_id: str, credentials: AdyenCredentials) -> AdyenCredentials:
        # NOTE (TOCTOU): the lock check and the upsert are two separate HTTP
        # calls, so a concurrent request could change `locked` between them.
        # The risk is low in practice (lock changes are rare admin operations),
        # but for a fully race-free guarantee this check should be enforced at
        # the database layer — e.g. via a Postgres trigger or stored procedure
        # that refuses to overwrite a row where locked = true.
        # TODO: move lock enforcement to a DB-level check (trigger/RPC).
        existing_credentials = self.get_adyen_config(user_id)
        if existing_credentials is not None and existing_credentials.locked:
            raise PermissionError("This configuration is locked and cannot be modified")

        response = http_requests.post(
            f"{self._base_url}/rest/v1/adyen_configs",
            headers={
                **self._headers,
                "Prefer": "resolution=merge-duplicates,return=representation",
            },
            json={
                "user_id": user_id,
                "api_key": credentials.api_key,
                "client_key": credentials.client_key,
                "merchant_account": credentials.merchant_account,
            },
            timeout=10,
        )
        response.raise_for_status()
        rows: list[dict[str, Any]] = response.json()
        row = rows[0]
        return AdyenCredentials(
            api_key=row["api_key"],
            client_key=row["client_key"],
            merchant_account=row["merchant_account"],
            environment=self._environment,
            locked=row.get("locked", False),
        )

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
        raw_role: str = rows[0].get("role", "user")
        try:
            return UserRole(raw_role)
        except ValueError:
            return UserRole.USER
