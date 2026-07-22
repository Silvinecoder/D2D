from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.helpers.model import Base, TimestampMixin

if TYPE_CHECKING:
    from .course_enrollment import CourseEnrollment


class CourseEnrollmentProgress(Base, TimestampMixin):
    __tablename__ = "course_enrollment_progress"

    course_enrollment_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("course_enrollments.id", ondelete="CASCADE"),
        primary_key=True,
    )

    progress_percentage: Mapped[int] = mapped_column(nullable=False, default=0)

    last_activity_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    passed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    final_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)

    enrollment: Mapped["CourseEnrollment"] = relationship(
        "CourseEnrollment",
        back_populates="progress",
    )
