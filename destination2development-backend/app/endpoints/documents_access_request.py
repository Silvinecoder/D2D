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
from app.schemas.document_access_request import (
    DocumentAccessRequestCreate,
    DocumentAccessRequestResponse,
)
from app.services.document_access_request_service import (
    AccessRequestAlreadyProcessedError,
    AccessRequestNotFoundError,
    DocumentAccessRequestService,
    PendingAccessRequestAlreadyExistsError,
)


router = APIRouter(
    prefix="/document-access-requests",
    tags=["document-access-requests"],
)


# CURRENT USER


@router.post(
    "",
    response_model=DocumentAccessRequestResponse,
)
def create_document_access_request(
    data: DocumentAccessRequestCreate,
    user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
):
    service = DocumentAccessRequestService(session)

    try:
        request = service.create_request(
            user=user,
            reason=data.reason,
        )

        session.commit()
        session.refresh(request)

        return request

    except PendingAccessRequestAlreadyExistsError:
        raise HTTPException(
            status_code=409,
            detail="Pending access request already exists.",
        )


# ADMIN


@router.get(
    "/admin",
    response_model=list[DocumentAccessRequestResponse],
)
def get_document_access_requests(
    session: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return DocumentAccessRequestService(session).list_requests()


@router.patch(
    "/admin/{request_id}/approve",
    response_model=DocumentAccessRequestResponse,
)
def approve_document_access_request(
    request_id: uuid.UUID,
    session: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = DocumentAccessRequestService(session)

    try:
        request = service.approve_request(
            request_id=request_id,
            reviewer=admin,
        )

        session.commit()
        session.refresh(request)

        return request

    except AccessRequestNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Access request not found.",
        )

    except AccessRequestAlreadyProcessedError:
        raise HTTPException(
            status_code=400,
            detail="Request already processed.",
        )


@router.patch(
    "/admin/{request_id}/reject",
    response_model=DocumentAccessRequestResponse,
)
def reject_document_access_request(
    request_id: uuid.UUID,
    session: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = DocumentAccessRequestService(session)

    try:
        request = service.reject_request(
            request_id=request_id,
            reviewer=admin,
        )

        session.commit()
        session.refresh(request)

        return request

    except AccessRequestNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Access request not found.",
        )

    except AccessRequestAlreadyProcessedError:
        raise HTTPException(
            status_code=400,
            detail="Request already processed.",
        )


# USER VIEW OWN REQUEST

@router.get(
    "/{request_id}",
    response_model=DocumentAccessRequestResponse,
)
def get_document_access_request(
    request_id: uuid.UUID,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    service = DocumentAccessRequestService(session)

    try:
        request = service.get_by_id_or_raise(request_id)

    except AccessRequestNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Access request not found.",
        )

    if request.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="Not allowed to view this request.",
        )

    return request