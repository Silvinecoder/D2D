from __future__ import annotations

import uuid
import enum

from typing import TYPE_CHECKING
from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.assistant.model_helper import Base, TimestampMixin

if TYPE_CHECKING:
    from .user import User


class UnlockRequestStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class UserUnlockRequest(Base, TimestampMixin):
    __tablename__ = "user_unlock_requests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    message: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    status: Mapped[UnlockRequestStatus] = mapped_column(
        Enum(
            UnlockRequestStatus,
            name="unlock_request_status",
        ),
        default=UnlockRequestStatus.pending,
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="unlock_requests",
    )
