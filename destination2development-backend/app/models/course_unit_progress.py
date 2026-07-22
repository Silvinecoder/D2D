from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.helpers.model import Base, TimestampMixin

if TYPE_CHECKING:
    from .course_enrollment import CourseEnrollment
    from .course_unit import CourseUnit


class UnitProgressStatus(str, enum.Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"


class CourseUnitProgress(Base, TimestampMixin):
    __tablename__ = "course_unit_progress"
    __table_args__ = (
        UniqueConstraint(
            "course_enrollment_id", "unit_id", name="uq_enrollment_unit_progress"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    course_enrollment_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("course_enrollments.id", ondelete="CASCADE"),
        nullable=False,
    )

    unit_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("course_units.id", ondelete="CASCADE"),
        nullable=False,
    )

    status: Mapped[UnitProgressStatus] = mapped_column(
        Enum(UnitProgressStatus, name="unit_progress_status"),
        nullable=False,
        default=UnitProgressStatus.not_started,
    )

    last_position_seconds: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    enrollment: Mapped["CourseEnrollment"] = relationship(
        "CourseEnrollment",
        back_populates="unit_progress",
    )

    unit: Mapped["CourseUnit"] = relationship(
        "CourseUnit",
        back_populates="unit_progress",
    )
