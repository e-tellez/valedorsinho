"""Admin router — user & role management (admin only)."""

import logging

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_auth_service, get_current_user
from app.api.schemas.admin import (
    ManagedUserResponse,
    UpdateUserRoleBody,
    UserListResponse,
)
from app.domain.models.auth import ManagedUser, UserProfile
from app.use_cases.auth_service import AuthService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["admin"])


def _to_response(user: ManagedUser) -> ManagedUserResponse:
    return ManagedUserResponse(user_id=user.user_id, email=user.email, role=user.role)


@router.get("/users", response_model=UserListResponse)
def list_users(
    current_user: UserProfile = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserListResponse:
    """Return every user with their role. Admin only."""
    try:
        users = auth_service.list_users(current_user)
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error))
    return UserListResponse(users=[_to_response(u) for u in users])


@router.put("/users/{user_id}/role", response_model=ManagedUserResponse)
def update_user_role(
    user_id: str,
    body: UpdateUserRoleBody,
    current_user: UserProfile = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> ManagedUserResponse:
    """Change a user's role. Admin only; cannot remove your own admin role."""
    try:
        updated = auth_service.set_user_role(current_user, user_id, body.role)
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return _to_response(updated)
