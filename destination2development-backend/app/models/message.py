from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.helpers.model import Base, TimestampMixin

if TYPE_CHECKING:
    from .message_thread import MessageThread
    from .user import User


class Message(Base, TimestampMixin):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    thread_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("message_threads.id", ondelete="CASCADE"),
        nullable=False,
    )

    sender_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    body: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    thread: Mapped["MessageThread"] = relationship(
        "MessageThread",
        back_populates="messages",
    )

    sender: Mapped["User"] = relationship(
        "User",
        back_populates="messages",
    )
