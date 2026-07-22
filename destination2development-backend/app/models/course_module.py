from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.helpers.model import Base, TimestampMixin

if TYPE_CHECKING:
    from .course import Course
    from .course_unit import CourseUnit


class CourseModule(Base, TimestampMixin):
    __tablename__ = "course_modules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    course_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)

    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    course: Mapped["Course"] = relationship(
        "Course",
        back_populates="modules",
    )

    units: Mapped[list["CourseUnit"]] = relationship(
        "CourseUnit",
        back_populates="module",
        cascade="all, delete-orphan",
        order_by="CourseUnit.sort_order",
    )
