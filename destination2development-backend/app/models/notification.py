from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.helpers.model import Base, TimestampMixin

if TYPE_CHECKING:
    from .user import User


class NotificationEventType(str, enum.Enum):
    message_sent = "message_sent"
    ticket_created = "ticket_created"
    ticket_reply = "ticket_reply"
    ticket_assigned = "ticket_assigned"
    document_verified = "document_verified"
    document_rejected = "document_rejected"
    document_access_approved = "document_access_approved"
    document_access_rejected = "document_access_rejected"


class NotificationEntityType(str, enum.Enum):
    thread = "thread"
    ticket = "ticket"
    message = "message"
    profile_document = "profile_document"


class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    event_type: Mapped[NotificationEventType] = mapped_column(
        Enum(
            NotificationEventType,
            name="notification_event_type",
        ),
        nullable=False,
    )

    entity_type: Mapped[NotificationEntityType] = mapped_column(
        Enum(
            NotificationEntityType,
            name="notification_entity_type",
        ),
        nullable=False,
    )

    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    body: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="notifications",
    )
