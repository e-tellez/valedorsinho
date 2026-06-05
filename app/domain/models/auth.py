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
class AdyenCredentials:
    api_key: str
    client_key: str
    merchant_account: str
    environment: str
    locked: bool = False
