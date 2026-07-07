from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_user,
    get_db,
    require_admin,
)
from app.models.user import User
from app.schemas.user_unlock_request import (
    UnlockRequestCreate,
    UnlockRequestResponse,
)
from app.services.user_unlock_request_service import (
    UserUnlockRequestService,
)


router = APIRouter(
    prefix="/unlock-requests",
    tags=["unlock requests"],
)


# USER CREATES REQUEST


@router.post(
    "",
    response_model=UnlockRequestResponse,
)
def create_unlock_request(
    data: UnlockRequestCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    request = UserUnlockRequestService(session).create_request(
        user=user,
        message=data.message,
    )
    session.commit()

    return request


# ADMIN LISTS REQUESTS


@router.get(
    "/admin",
    response_model=list[UnlockRequestResponse],
)
def list_unlock_requests(
    session: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return UserUnlockRequestService(session).get_pending_requests()


# ADMIN APPROVES


@router.patch(
    "/admin/{request_id}/approve",
    response_model=UnlockRequestResponse,
)
def approve_unlock_request(
    request_id: uuid.UUID,
    session: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    request = UserUnlockRequestService(session).approve_request(
        request_id,
    )
    session.commit()

    return request


# ADMIN REJECTS


@router.patch(
    "/admin/{request_id}/reject",
    response_model=UnlockRequestResponse,
)
def reject_unlock_request(
    request_id: uuid.UUID,
    session: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    request = UserUnlockRequestService(session).reject_request(
        request_id,
    )
    session.commit()

    return request
