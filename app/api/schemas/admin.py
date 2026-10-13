"""Pydantic schemas for the admin user-management endpoints."""

from __future__ import annotations

from pydantic import BaseModel
from pydantic.alias_generators import to_camel

from app.domain.models.auth import UserRole


class ManagedUserResponse(BaseModel):
    model_config = {"alias_generator": to_camel, "populate_by_name": True}

    user_id: str
    email: str
    role: UserRole


class UserListResponse(BaseModel):
    users: list[ManagedUserResponse]


class UpdateUserRoleBody(BaseModel):
    role: UserRole
