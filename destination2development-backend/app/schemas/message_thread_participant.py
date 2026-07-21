from __future__ import annotations

import uuid

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AddMessageThreadParticipantRequest(BaseModel):
    thread_id: uuid.UUID
    user_id: uuid.UUID


class RemoveMessageThreadParticipantRequest(BaseModel):
    thread_id: uuid.UUID
    user_id: uuid.UUID


class MessageThreadParticipantResponse(BaseModel):
    id: uuid.UUID
    thread_id: uuid.UUID
    user_id: uuid.UUID
    joined_at: datetime

    model_config = {
        "from_attributes": True,
    }
