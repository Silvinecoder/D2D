from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    String,
    Boolean,
    ARRAY,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.helpers.model import Base, TimestampMixin


if TYPE_CHECKING:
    from .business import Business
    from .category import Category
    from .course_enrollment import CourseEnrollment
    from .course_price import CoursePrice
    from .user import User
    from .course_language import CourseLanguage
    from .course_module import CourseModule


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
        String(255),
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    highlights: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        default=list,
        server_default="{}",
    )

    image: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    duration_minutes: Mapped[int] = mapped_column(
        nullable=False,
    )

    has_coursework: Mapped[bool] = mapped_column(
        Boolean,
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

    business: Mapped["Business"] = relationship(
        "Business",
        back_populates="courses",
    )

    category: Mapped["Category"] = relationship(
        "Category",
        back_populates="courses",
    )

    languages: Mapped[list["CourseLanguage"]] = relationship(
        "CourseLanguage",
        back_populates="course",
        cascade="all, delete-orphan",
    )
    creator: Mapped["User"] = relationship(
        "User",
        back_populates="created_courses",
    )

    modules: Mapped[list["CourseModule"]] = relationship(
        "CourseModule",
        back_populates="course",
        cascade="all, delete-orphan",
        order_by="CourseModule.sort_order",
    )

    prices: Mapped[list["CoursePrice"]] = relationship(
        "CoursePrice",
        back_populates="course",
        cascade="all, delete-orphan",
    )

    enrollments: Mapped[list["CourseEnrollment"]] = relationship(
        "CourseEnrollment",
        back_populates="course",
        cascade="all, delete-orphan",
    )