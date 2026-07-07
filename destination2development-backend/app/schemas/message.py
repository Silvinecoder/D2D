from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class CreateMessageRequest(BaseModel):
    body: str


class MessageResponse(BaseModel):
    id: uuid.UUID
    thread_id: uuid.UUID
    sender_id: uuid.UUID
    body: str
    read_at: datetime | None

    model_config = {
        "from_attributes": True,
    }
