from __future__ import annotations

import uuid

from pydantic import BaseModel

from app.models.user_unlock_request import (
    UnlockRequestStatus,
)


class UnlockRequestCreate(BaseModel):
    message: str


class UnlockRequestResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    message: str
    status: UnlockRequestStatus

    model_config = {
        "from_attributes": True,
    }
