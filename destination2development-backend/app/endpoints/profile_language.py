from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_active_user,
    get_db,
)
from app.models.user import User
from app.schemas.profile_language import (
    ProfileLanguageCreate,
    ProfileLanguageResponse,
)
from app.services.profile_language import (
    LanguageNotFoundError,
    ProfileLanguageService,
)
from app.services.profile import (
    ProfileNotFoundError,
    ProfileService,
)

router = APIRouter(
    prefix="/profile/languages",
    tags=["profile-languages"],
)


@router.get(
    "",
    response_model=list[ProfileLanguageResponse],
)
def get_profile_languages(
    user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
):
    try:
        profile = ProfileService(session).get_profile_or_raise(
            user.id,
        )

        return ProfileLanguageService(session).get_profile_languages(
            profile.id,
        )

    except ProfileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Profile not found.",
        )


@router.post(
    "",
    response_model=ProfileLanguageResponse,
)
def add_profile_language(
    data: ProfileLanguageCreate,
    user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
):
    try:
        profile = ProfileService(session).get_profile_or_raise(
            user.id,
        )

        profile_language = ProfileLanguageService(session).add_language(
            profile_id=profile.id,
            language_id=data.language_id,
            language_type=data.type,
        )

        session.commit()
        session.refresh(profile_language)

        return profile_language

    except ProfileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Profile not found.",
        )

    except LanguageNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Language not found.",
        )


@router.delete("")
def remove_profile_language(
    data: ProfileLanguageCreate,
    user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
):
    try:
        profile = ProfileService(session).get_profile_or_raise(
            user.id,
        )

        ProfileLanguageService(session).remove_language(
            profile_id=profile.id,
            language_id=data.language_id,
            language_type=data.type,
        )

        session.commit()

        return {
            "message": "Language removed successfully.",
        }

    except ProfileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Profile not found.",
        )
