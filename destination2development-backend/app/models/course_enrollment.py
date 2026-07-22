from __future__ import annotations

import uuid
import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.helpers.model import Base, TimestampMixin


if TYPE_CHECKING:
    from .course import Course
    from .user import User


class CourseEnrollmentStatus(str, enum.Enum):
    enrolled = "enrolled"
    active = "active"
    completed = "completed"
    suspended = "suspended"
    dropped = "dropped"


class CourseEnrollment(Base, TimestampMixin):
    __tablename__ = "course_enrollments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    reference_number: Mapped[str | None] = mapped_column(
        String, unique=True, nullable=True
    )
    status: Mapped[CourseEnrollmentStatus] = mapped_column(
        Enum(CourseEnrollmentStatus, name="course_enrollment_status"),
        nullable=False,
        default=CourseEnrollmentStatus.enrolled,
    )
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    course: Mapped["Course"] = relationship("Course", back_populates="enrollments")
    user: Mapped["User"] = relationship("User", back_populates="course_enrollments")

    progress: Mapped["CourseEnrollmentProgress | None"] = relationship(
        "CourseEnrollmentProgress",
        back_populates="enrollment",
        uselist=False,
        cascade="all, delete-orphan",
        single_parent=True,
    )
