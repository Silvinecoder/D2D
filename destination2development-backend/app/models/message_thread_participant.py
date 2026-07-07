from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.assistant.model_helper import Base, TimestampMixin

if TYPE_CHECKING:
    from .message_thread import MessageThread
    from .user import User


class ParticipantRole(str, enum.Enum):
    student = "student"
    assessor = "assessor"
    admin = "admin"
    support = "support"


class MessageThreadParticipant(Base, TimestampMixin):
    __tablename__ = "message_thread_participants"

    __table_args__ = (
        UniqueConstraint(
            "thread_id",
            "user_id",
            name="uq_message_thread_participant",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    thread_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "message_threads.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    role: Mapped[ParticipantRole] = mapped_column(
        Enum(
            ParticipantRole,
            name="participant_role",
        ),
        nullable=False,
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    thread: Mapped["MessageThread"] = relationship(
        "MessageThread",
        back_populates="participants",
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="thread_participations",
    )
