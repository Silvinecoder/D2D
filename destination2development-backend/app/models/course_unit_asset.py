from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.helpers.model import Base, TimestampMixin

if TYPE_CHECKING:
    from .course_unit import CourseUnit


class AssetType(str, enum.Enum):
    video = "video"
    document = "document"
    pdf = "pdf"
    scorm = "scorm"
    audio = "audio"
    image = "image"


class CourseUnitAsset(Base, TimestampMixin):
    __tablename__ = "course_unit_assets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    unit_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("course_units.id", ondelete="CASCADE"),
        nullable=False,
    )

    asset_type: Mapped[AssetType] = mapped_column(
        String(50),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)

    s3_key: Mapped[str] = mapped_column(String, nullable=False)

    asset_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )

    unit: Mapped["CourseUnit"] = relationship(
        "CourseUnit",
        back_populates="assets",
    )
