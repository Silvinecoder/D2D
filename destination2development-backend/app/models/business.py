from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.helpers.model import Base, TimestampMixin

if TYPE_CHECKING:
    from .user import User
    from .course import Course


class BusinessRole(str, enum.Enum):
    owner = "owner"
    editor = "editor"


class Business(Base, TimestampMixin):
    __tablename__ = "businesses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    logo: Mapped[str | None] = mapped_column(String, nullable=True)

    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="business",
    )

    courses: Mapped[list["Course"]] = relationship(
        "Course",
        back_populates="business",
        cascade="all, delete-orphan",
    )
