from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.helpers.model import Base, TimestampMixin

if TYPE_CHECKING:
    from .business import Business
    from .category import Category
    from .course_enrollment import CourseEnrollment
    from .course_faq import CourseFaq
    from .course_price import CoursePrice
    from .user import User


class CourseLevel(str, enum.Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class CourseStatus(str, enum.Enum):
    draft = "draft"
    published = "published"
    archived = "archived"


class Course(Base, TimestampMixin):
    __tablename__ = "courses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    business_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
    )

    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("course_categories.id", ondelete="RESTRICT"),
        nullable=False,
    )

    created_by_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    image: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    level: Mapped[CourseLevel] = mapped_column(
        Enum(
            CourseLevel,
            name="course_level",
        ),
        nullable=False,
    )

    language: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    duration: Mapped[int] = mapped_column(
        nullable=False,
    )

    status: Mapped[CourseStatus] = mapped_column(
        Enum(
            CourseStatus,
            name="course_status",
        ),
        nullable=False,
        default=CourseStatus.draft,
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    category: Mapped["Category"] = relationship(
        "Category",
        back_populates="courses",
    )

    prices: Mapped[list["CoursePrice"]] = relationship(
        "CoursePrice",
        back_populates="course",
        cascade="all, delete-orphan",
    )

    faqs: Mapped[list["CourseFaq"]] = relationship(
        "CourseFaq",
        back_populates="course",
        cascade="all, delete-orphan",
        order_by="CourseFaq.sort_order",
    )

    enrollments: Mapped[list["CourseEnrollment"]] = relationship(
        "CourseEnrollment",
        back_populates="course",
        cascade="all, delete-orphan",
    )

    business: Mapped["Business"] = relationship(
        "Business",
        back_populates="courses",
    )

    creator: Mapped["User"] = relationship(
        "User",
        back_populates="created_courses",
    )
