from __future__ import annotations

import uuid

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.message_thread_participant import ParticipantRole


class AddMessageThreadParticipantRequest(BaseModel):
    thread_id: uuid.UUID
    user_id: uuid.UUID
    role: ParticipantRole


class RemoveMessageThreadParticipantRequest(BaseModel):
    thread_id: uuid.UUID
    user_id: uuid.UUID


class MessageThreadParticipantResponse(BaseModel):
    id: uuid.UUID
    thread_id: uuid.UUID
    user_id: uuid.UUID
    role: ParticipantRole
    joined_at: datetime

    model_config = {
        "from_attributes": True,
    }
