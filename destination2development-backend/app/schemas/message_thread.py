from __future__ import annotations

import uuid

from pydantic import BaseModel

from app.models.message_thread import (
    MessageThreadType,
    TicketStatus,
)


class CreateMessageThreadRequest(BaseModel):
    message_type: MessageThreadType
    subject: str | None = None


class MessageThreadResponse(BaseModel):
    id: uuid.UUID
    message_type: MessageThreadType
    subject: str | None
    status: TicketStatus | None
    created_by: uuid.UUID
    last_message_at: datetime | None

    model_config = {
        "from_attributes": True,
    }
