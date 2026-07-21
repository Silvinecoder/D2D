from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.helpers.model import Base, TimestampMixin

if TYPE_CHECKING:
    from .user import User
    from .course import Course

class BusinessRole(str, enum.Enum):
    owner = "owner"
    editor = "editor"


class BusinessUser(Base, TimestampMixin):
    __tablename__ = "business_users"

    business_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"),
        primary_key=True,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    role: Mapped[BusinessRole] = mapped_column(
        Enum(
            BusinessRole,
            name="business_role",
        ),
        nullable=False,
        default=BusinessRole.editor,
    )

    business: Mapped["Business"] = relationship(
        "Business",
        back_populates="users",
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="businesses",
    )
