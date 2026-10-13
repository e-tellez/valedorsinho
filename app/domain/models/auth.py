"""Authentication and credential domain models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    IM = "im"
    USER = "user"


@dataclass(frozen=True)
class UserProfile:
    user_id: str
    email: str
    role: UserRole


@dataclass(frozen=True)
class ManagedUser:
    """A user as seen by an admin in the user-management panel."""

    user_id: str
    email: str
    role: UserRole


@dataclass(frozen=True)
class AdyenCredentials:
    api_key: str
    client_key: str
    merchant_account: str
    environment: str
    locked: bool = False


@dataclass(frozen=True)
class AdyenAccount:
    """Metadata for one of a user's saved Adyen company accounts.

    Used by the account-management panel. Never carries the secret API key —
    only whether one is configured (``api_key_configured``).
    """

    id: str
    label: str
    client_key: str
    merchant_account: str
    is_active: bool
    locked: bool
    api_key_configured: bool
