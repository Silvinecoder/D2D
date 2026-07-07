from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.profile_document import (
    DocumentType,
    VerificationStatus,
)


class ProfileDocumentCreate(BaseModel):
    document_type: DocumentType
    file_path: str


class ProfileDocumentResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID

    document_type: DocumentType
    file_path: str

    verification_status: VerificationStatus

    verified_by: uuid.UUID | None
    verified_at: datetime | None

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }
