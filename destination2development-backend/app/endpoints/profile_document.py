from __future__ import annotations

import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_user,
    get_db,
    require_admin,
)
from app.models.user import User
from app.models.profile_document import VerificationStatus
from app.schemas.profile_document import (
    ProfileDocumentCreate,
    ProfileDocumentResponse,
)
from app.services.profile_document import (
    DocumentAlreadyExistsError,
    DocumentNotFoundError,
    InvalidDocumentStateError,
    ProfileDocumentService,
)


router = APIRouter(
    prefix="/profile-documents",
    tags=["profile-documents"],
)


# USER


@router.post(
    "",
    response_model=ProfileDocumentResponse,
)
def upload_document(
    data: ProfileDocumentCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    try:
        document = ProfileDocumentService(session).upload_document(
            user=user,
            document_type=data.document_type,
            file_path=data.file_path,
        )

        session.commit()

        return document

    except DocumentAlreadyExistsError:
        raise HTTPException(
            status_code=409,
            detail="Document already exists.",
        )


@router.get(
    "",
    response_model=list[ProfileDocumentResponse],
)
def get_my_documents(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    return ProfileDocumentService(session).list_documents(
        user_id=user.id,
    )


# ADMIN


@router.patch(
    "/admin/{document_id}/review",
    response_model=ProfileDocumentResponse,
)
def mark_document_in_review(
    document_id: uuid.UUID,
    admin: User = Depends(require_admin),
    session: Session = Depends(get_db),
):
    try:
        document = ProfileDocumentService(session).mark_in_review(
            document_id,
            admin,
        )

        session.commit()

        return document

    except DocumentNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    except InvalidDocumentStateError:
        raise HTTPException(
            status_code=400,
            detail="Invalid document state.",
        )


@router.get(
    "/admin",
    response_model=list[ProfileDocumentResponse],
)
def get_documents(
    status: VerificationStatus | None = None,
    session: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return ProfileDocumentService(session).list_documents(
        status=status,
    )


@router.patch(
    "/admin/{document_id}/approve",
    response_model=ProfileDocumentResponse,
)
def approve_document(
    document_id: uuid.UUID,
    admin: User = Depends(require_admin),
    session: Session = Depends(get_db),
):
    try:
        document = ProfileDocumentService(session).approve_document(
            document_id,
            admin,
        )

        session.commit()

        return document

    except DocumentNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    except InvalidDocumentStateError:
        raise HTTPException(
            status_code=400,
            detail="Invalid document state.",
        )


@router.patch(
    "/admin/{document_id}/reject",
    response_model=ProfileDocumentResponse,
)
def reject_document(
    document_id: uuid.UUID,
    admin: User = Depends(require_admin),
    session: Session = Depends(get_db),
):
    try:
        document = ProfileDocumentService(session).reject_document(
            document_id,
            admin,
        )

        session.commit()

        return document

    except DocumentNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    except InvalidDocumentStateError:
        raise HTTPException(
            status_code=400,
            detail="Invalid document state.",
        )
