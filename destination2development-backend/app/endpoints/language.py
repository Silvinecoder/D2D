from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.language import LanguageResponse
from app.services.language import (
    LanguageNotFoundError,
    LanguageService,
)


router = APIRouter(
    prefix="/languages",
    tags=["languages"],
)


@router.get(
    "",
    response_model=list[LanguageResponse],
)
def list_languages(
    session: Session = Depends(get_db),
):
    return LanguageService(session).list_languages()


@router.get(
    "/{language_id}",
    response_model=LanguageResponse,
)
def get_language(
    language_id: uuid.UUID,
    session: Session = Depends(get_db),
):
    service = LanguageService(session)

    try:
        return service.get_by_id_or_raise(language_id)

    except LanguageNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Language not found.",
        )
