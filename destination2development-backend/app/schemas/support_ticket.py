from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.support_ticket import TicketStatus


class CreateSupportTicketRequest(BaseModel):
    subject: str


class UpdateTicketStatusRequest(BaseModel):
    status: TicketStatus


class AssignTicketRequest(BaseModel):
    admin_id: uuid.UUID


class SupportTicketResponse(BaseModel):
    id: uuid.UUID
    thread_id: uuid.UUID
    status: TicketStatus
    assigned_admin_id: uuid.UUID | None
    resolved_at: datetime | None
    closed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }