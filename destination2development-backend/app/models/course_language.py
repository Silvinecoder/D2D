from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.helpers.model import Base, TimestampMixin


if TYPE_CHECKING:
    from .course import Course
    from .language import Language


class CourseLanguage(Base, TimestampMixin):
    __tablename__ = "course_languages"

    course_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"),
        primary_key=True,
    )

    language_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("languages.id", ondelete="RESTRICT"),
        primary_key=True,
    )

    course: Mapped["Course"] = relationship(
        "Course",
        back_populates="languages",
    )

    language: Mapped["Language"] = relationship(
        "Language",
        back_populates="courses",
    )