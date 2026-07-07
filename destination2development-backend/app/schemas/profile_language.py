from __future__ import annotations

import uuid

from pydantic import BaseModel

from app.models.profile_language import LanguageType
from app.schemas.language import LanguageResponse


class ProfileLanguageCreate(BaseModel):
    language_id: uuid.UUID
    type: LanguageType


class ProfileLanguageResponse(BaseModel):
    profile_id: uuid.UUID
    language: LanguageResponse
    type: LanguageType

    model_config = {
        "from_attributes": True,
    }
