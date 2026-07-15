from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_active_user,
    get_current_user,
    get_db,
    require_admin,
)
from app.models.user import User
from app.schemas.user import (
    UserEmailUpdate,
    UserNameUpdate,
    UserPasswordUpdate,
    UserResponse,
    UserRoleUpdate,
)
from app.services.user_auth0 import Auth0Service
from app.services.user import (
    UserNotFoundError,
    UserService,
)


router = APIRouter(
    prefix="/users",
    tags=["users"],
)

auth0 = Auth0Service()


# CURRENT USER


@router.get(
    "/current",
    response_model=UserResponse,
)
def get_current_user_details(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    # get_current_user may have just bumped last_login_at.
    session.commit()

    return user


@router.patch(
    "/current/name",
    response_model=UserResponse,
)
def update_current_user_name(
    data: UserNameUpdate,
    user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
):
    try:
        auth0.update_name(user.auth0_id, data.name)

        user = UserService(session).update_user_name(
            user.id,
            data.name,
        )

        session.commit()

        return user

    except UserNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )


@router.patch(
    "/current/email",
    response_model=UserResponse,
)
def update_current_user_email(
    data: UserEmailUpdate,
    user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
):
    try:
        auth0.update_email(user.auth0_id, data.email)

        user = UserService(session).update_user_email(
            user.id,
            data.email,
        )

        session.commit()

        return user

    except UserNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )


@router.patch(
    "/current/password",
)
def update_current_user_password(
    data: UserPasswordUpdate,
    user: User = Depends(get_current_active_user),
):
    auth0.update_password(user.auth0_id, data.password)

    return {
        "message": "Password updated successfully.",
    }


@router.delete(
    "/current",
    response_model=UserResponse,
)
def delete_current_user(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    try:
        user = UserService(session).schedule_deletion(user.id)

        session.commit()

        return user

    except UserNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )


# ADMIN


@router.get(
    "/admin",
    response_model=list[UserResponse],
)
def get_users(
    session: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return UserService(session).get_all_users()


@router.get(
    "/admin/{user_id}",
    response_model=UserResponse,
)
def get_user(
    user_id: uuid.UUID,
    session: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    try:
        return UserService(session).get_by_id(user_id)

    except UserNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )


@router.patch(
    "/admin/{user_id}/role",
    response_model=UserResponse,
)
def update_user_role(
    user_id: uuid.UUID,
    data: UserRoleUpdate,
    session: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    try:
        user = UserService(session).set_role(
            user_id,
            data.system_role,
        )

        session.commit()

        return user

    except UserNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )


@router.patch(
    "/admin/{user_id}/lock",
    response_model=UserResponse,
)
def lock_user(
    user_id: uuid.UUID,
    session: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    try:
        user = UserService(session).lock_user(user_id)

        session.commit()

        return user

    except UserNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )


@router.patch(
    "/admin/{user_id}/deactivate",
    response_model=UserResponse,
)
def deactivate_user(
    user_id: uuid.UUID,
    session: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    try:
        user = UserService(session).schedule_deletion(user_id)

        session.commit()

        return user

    except UserNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )


@router.patch(
    "/admin/{user_id}/restore",
    response_model=UserResponse,
)
def restore_user(
    user_id: uuid.UUID,
    session: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    try:
        user = UserService(session).restore_user(user_id)

        session.commit()

        return user

    except UserNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )


@router.post(
    "/admin/process-deletions",
    response_model=list[UserResponse],
)
def process_scheduled_deletions(
    session: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """Permanently deletes users whose scheduled_deletion_at has passed.

    UserService already had get_users_ready_for_deletion() and
    permanently_delete_user(), but nothing ever called them, so
    scheduled deletions were never actually carried out. Snapshot each
    user into a response before deleting, since there's nothing left
    to serialize afterward.
    """
    service = UserService(session)

    users = service.get_users_ready_for_deletion()

    deleted = [UserResponse.model_validate(user) for user in users]

    for user in users:
        service.permanently_delete_user(user.id)

    session.commit()

    return deleted
