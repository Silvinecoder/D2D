from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_user,
    get_db,
)
from app.models.user import User
from app.schemas.profile import (
    ProfileCreate,
    ProfileResponse,
    ProfileUpdate,
)
from app.services.profile_service import (
    InvalidAvatarDocumentError,
    ProfileAlreadyExistsError,
    ProfileNotFoundError,
    ProfileService,
)

router = APIRouter(
    prefix="/profile",
    tags=["profile"],
)


@router.post(
    "",
    response_model=ProfileResponse,
)
def create_profile(
    data: ProfileCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    try:
        profile = ProfileService(session).create_profile(
            user=user,
            qualification=data.qualification,
            avatar_document_id=data.avatar_document_id,
            date_of_birth=data.date_of_birth,
            gender=data.gender,
            city=data.city,
            education_level=data.education_level,
        )

        session.commit()

        return profile

    except ProfileAlreadyExistsError:
        raise HTTPException(
            status_code=409,
            detail="Profile already exists.",
        )

    except InvalidAvatarDocumentError:
        raise HTTPException(
            status_code=400,
            detail="Invalid avatar document.",
        )


@router.get(
    "",
    response_model=ProfileResponse,
)
def get_profile(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    try:
        return ProfileService(session).get_profile_or_raise(user.id)

    except ProfileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Profile not found.",
        )


@router.patch(
    "",
    response_model=ProfileResponse,
)
def update_profile(
    data: ProfileUpdate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    try:
        profile = ProfileService(session).update_profile(
            user.id,
            qualification=data.qualification,
            avatar_document_id=data.avatar_document_id,
            date_of_birth=data.date_of_birth,
            gender=data.gender,
            city=data.city,
            education_level=data.education_level,
        )

        session.commit()

        return profile

    except ProfileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Profile not found.",
        )

    except InvalidAvatarDocumentError:
        raise HTTPException(
            status_code=400,
            detail="Invalid avatar document.",
        )
