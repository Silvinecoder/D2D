from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.helpers.model import Base, TimestampMixin

if TYPE_CHECKING:
    from .profile_document import ProfileDocument
    from .profile_language import ProfileLanguage
    from .user import User


class Profile(Base, TimestampMixin):
    __tablename__ = "profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
    )

    qualification: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    avatar_document_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("profile_documents.id"),
        nullable=True,
    )

    date_of_birth: Mapped[date | None] = mapped_column(nullable=True)

    gender: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    city: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    education_level: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    user: Mapped[User] = relationship(
        "User",
        back_populates="profile",
    )

    avatar_document: Mapped[ProfileDocument | None] = relationship(
        "ProfileDocument",
        foreign_keys=[avatar_document_id],
    )

    profile_languages: Mapped[list[ProfileLanguage]] = relationship(
        "ProfileLanguage",
        back_populates="profile",
        cascade="all, delete-orphan",
    )
