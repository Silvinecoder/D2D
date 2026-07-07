from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.document_access_request import Status


class DocumentAccessRequestCreate(BaseModel):
    reason: str | None = None


class DocumentAccessRequestResponse(BaseModel):
    id: uuid.UUID

    user_id: uuid.UUID

    reason: str | None

    status: Status

    requested_at: datetime

    reviewed_at: datetime | None

    reviewed_by: uuid.UUID | None

    model_config = {
        "from_attributes": True,
    }
