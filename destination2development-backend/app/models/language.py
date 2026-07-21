from __future__ import annotations

import uuid

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.helpers.model import Base, TimestampMixin

if TYPE_CHECKING:
    from .profile_language import ProfileLanguage
    from .course_language import CourseLanguage


class Language(Base, TimestampMixin):
    __tablename__ = "languages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    code: Mapped[str] = mapped_column(
        String(10),
        unique=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    courses: Mapped[list["CourseLanguage"]] = relationship(
        "CourseLanguage",
        back_populates="language",
        cascade="all, delete-orphan",
    )

    profile_languages: Mapped[list["ProfileLanguage"]] = relationship(
        "ProfileLanguage",
        back_populates="language",
    )
