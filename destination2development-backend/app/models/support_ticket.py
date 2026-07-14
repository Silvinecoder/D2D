from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.assistant.model_helper import Base, TimestampMixin

if TYPE_CHECKING:
    from .message_thread import MessageThread
    from .user import User


class TicketStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    pending = "pending"
    resolved = "resolved"
    closed = "closed"


_TICKET_TRANSITIONS: dict[TicketStatus, frozenset[TicketStatus]] = {
    TicketStatus.open: frozenset(
        {
            TicketStatus.in_progress,
            TicketStatus.pending,
            TicketStatus.closed,
        }
    ),
    TicketStatus.in_progress: frozenset(
        {
            TicketStatus.pending,
            TicketStatus.resolved,
            TicketStatus.closed,
        }
    ),
    TicketStatus.pending: frozenset(
        {
            TicketStatus.in_progress,
            TicketStatus.resolved,
            TicketStatus.closed,
        }
    ),
    TicketStatus.resolved: frozenset(
        {
            TicketStatus.in_progress,
            TicketStatus.closed,
        }
    ),
    TicketStatus.closed: frozenset(
        {
            TicketStatus.open,
        }
    ),
}

# Guards against a future TicketStatus member being added without a
# corresponding transitions entry — fails at import time, not at runtime
# on a real user's request.
assert set(_TICKET_TRANSITIONS) == set(TicketStatus), (
    "_TICKET_TRANSITIONS is missing an entry for a TicketStatus member"
)


def can_transition(current: TicketStatus, target: TicketStatus) -> bool:
    if current == target:
        return True
    return target in _TICKET_TRANSITIONS[current]


def allowed_next_statuses(current: TicketStatus) -> frozenset[TicketStatus]:
    return _TICKET_TRANSITIONS[current]


class SupportTicket(Base, TimestampMixin):
    __tablename__ = "support_tickets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    thread_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("message_threads.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    status: Mapped[TicketStatus] = mapped_column(
        Enum(TicketStatus, name="ticket_status"),
        default=TicketStatus.open,
        nullable=False,
    )

    assigned_admin_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    thread: Mapped["MessageThread"] = relationship(
        "MessageThread",
        back_populates="ticket",
        single_parent=True,
    )

    assigned_admin: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[assigned_admin_id],
        back_populates="assigned_tickets",
    )
