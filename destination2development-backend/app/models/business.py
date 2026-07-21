from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.helpers.model import Base, TimestampMixin

if TYPE_CHECKING:
    from .user import User
    from .course import Course


class Business(Base, TimestampMixin):
    __tablename__ = "businesses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    slug: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    logo: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    users: Mapped[list["BusinessUser"]] = relationship(
        "BusinessUser",
        back_populates="business",
        cascade="all, delete-orphan",
    )

    courses: Mapped[list["Course"]] = relationship(
        "Course",
        back_populates="business",
        cascade="all, delete-orphan",
    )
    