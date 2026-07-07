from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel


class ProfileCreate(BaseModel):
    qualification: str | None = None
    avatar_document_id: uuid.UUID | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    city: str | None = None
    education_level: str | None = None


class ProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID

    qualification: str | None
    avatar_document_id: uuid.UUID | None
    date_of_birth: date | None
    gender: str | None
    city: str | None
    education_level: str | None

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }


class ProfileUpdate(BaseModel):
    qualification: str | None = None
    avatar_document_id: uuid.UUID | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    city: str | None = None
    education_level: str | None = None
