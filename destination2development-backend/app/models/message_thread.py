from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.assistant.model_helper import Base

if TYPE_CHECKING:
    from .message import Message
    from .message_thread_participant import MessageThreadParticipant
    from .user import User


class MessageThreadType(str, enum.Enum):
    chat = "chat"
    ticket = "ticket"


class TicketStatus(str, enum.Enum):
    open = "open"
    pending = "pending"
    resolved = "resolved"
    closed = "closed"

class MessageThread(Base, TimestampMixin):
    __tablename__ = "message_threads"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    message_type: Mapped[MessageThreadType] = mapped_column(
        Enum(
            MessageThreadType,
            name="message_thread_type",
        ),
        nullable=False,
    )

    subject: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    status: Mapped[TicketStatus | None] = mapped_column(
        Enum(
            TicketStatus,
            name="ticket_status",
        ),
        nullable=True,
    )

    created_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    last_message_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    creator: Mapped["User"] = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="created_message_threads",
    )

    participants: Mapped[list["MessageThreadParticipant"]] = relationship(
        "MessageThreadParticipant",
        back_populates="thread",
        cascade="all, delete-orphan",
    )

    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="thread",
        cascade="all, delete-orphan",
    )