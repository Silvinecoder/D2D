from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.helpers.model import Base, TimestampMixin

if TYPE_CHECKING:
    from .course_module import CourseModule
    from .course_unit_progress import CourseUnitProgress
    from .course_unit_asset import CourseUnitAsset


class CourseUnit(Base, TimestampMixin):
    __tablename__ = "course_units"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    module_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("course_modules.id", ondelete="CASCADE"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)

    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    module: Mapped["CourseModule"] = relationship(
        "CourseModule",
        back_populates="units",
    )

    unit_progress: Mapped[list["CourseUnitProgress"]] = relationship(
        "CourseUnitProgress",
        back_populates="unit",
        cascade="all, delete-orphan",
    )

    assets: Mapped[list["CourseUnitAsset"]] = relationship(
        "CourseUnitAsset",
        back_populates="unit",
        cascade="all, delete-orphan",
        order_by="CourseUnitAsset.sort_order",
    )
