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
    UserAccountTypeUpdate,
    UserBusinessAssignmentUpdate,
    UserBusinessRoleUpdate,
)
from app.services.user_auth0 import Auth0Service
from app.services.user import (
    AccountNotDeactivatedError,
    BusinessNotFoundError,
    BusinessRoleRequiredError,
    UserNotFoundError,
    UserService,
    AccountTypeAlreadySetError,
)
from app.services.account_deletion import AccountDeletionService


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
    "/current/account-type",
    response_model=UserResponse,
)
def update_current_user_account_type(
    data: UserAccountTypeUpdate,
    user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
):
    try:
        user = UserService(session).set_account_type(
            user.id,
            data.account_type,
        )

        session.commit()
        session.refresh(user)

        return user

    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found.")

    except AccountTypeAlreadySetError:
        raise HTTPException(
            status_code=409,
            detail="Account type has already been selected.",
        )


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
def deactivate_current_user(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    try:
        user = AccountDeletionService(session).deactivate(
            user.id,
        )

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
    "/admin/{user_id}/restore",
    response_model=UserResponse,
)
def restore_user(
    user_id: uuid.UUID,
    session: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    try:
        user = AccountDeletionService(session).restore(user_id)

        session.commit()

        return user

    except UserNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )
    except AccountNotDeactivatedError:
        raise HTTPException(
            status_code=409,
            detail="User account is not deactivated.",
        )


@router.delete(
    "/admin/{user_id}",
    response_model=UserResponse,
)
def delete_user(
    user_id: uuid.UUID,
    session: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    try:
        user = AccountDeletionService(session).permanently_delete(user_id)

        response = UserResponse.model_validate(user)

        session.commit()

        return response

    except UserNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

@router.patch(
    "/admin/{user_id}/business",
    response_model=UserResponse,
)
def assign_user_to_business(
    user_id: uuid.UUID,
    data: UserBusinessAssignmentUpdate,
    session: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    try:
        user = UserService(session).set_account_type(
            user_id,
            AccountType.business,
            business_id=data.business_id,
            business_role=data.business_role,
        )

        session.commit()
        session.refresh(user)

        return user

    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found.")
    except BusinessNotFoundError:
        raise HTTPException(status_code=404, detail="Business not found.")
    except BusinessRoleRequiredError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch(
    "/admin/{user_id}/business/role",
    response_model=UserResponse,
)
def update_user_business_role(
    user_id: uuid.UUID,
    data: UserBusinessRoleUpdate,
    session: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    try:
        user = UserService(session).change_business_role(
            user_id,
            data.business_role,
        )

        session.commit()
        session.refresh(user)

        return user

    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found.")
    except BusinessRoleRequiredError as e:
        raise HTTPException(status_code=400, detail=str(e))