from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID

    event_type: str
    entity_type: str
    entity_id: uuid.UUID

    title: str
    body: str

    created_at: datetime
    read_at: datetime | None

    model_config = {
        "from_attributes": True,
    }


class NotificationListResponse(BaseModel):
    items: list[NotificationResponse]
    unread_count: int

    model_config = {
        "from_attributes": True,
    }
