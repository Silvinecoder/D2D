from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.helpers.model import Base, TimestampMixin

if TYPE_CHECKING:
    from .language import Language
    from .profile import Profile


class LanguageType(str, enum.Enum):
    learning = "learning"
    teaching = "teaching"


class ProfileLanguage(Base, TimestampMixin):
    __tablename__ = "profile_languages"

    profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("profiles.id"),
        primary_key=True,
    )

    language_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("languages.id"),
        primary_key=True,
    )

    type: Mapped[LanguageType] = mapped_column(
        Enum(LanguageType, name="language_type"),
        nullable=False,
    )

    profile: Mapped[Profile] = relationship(
        "Profile",
        back_populates="profile_languages",
    )

    language: Mapped[Language] = relationship(
        "Language",
        back_populates="profile_languages",
    )
