from __future__ import annotations

import enum
import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.helpers.model import Base, TimestampMixin

if TYPE_CHECKING:
    from .course import Course


class DeliveryType(str, enum.Enum):
    online = "online"
    in_person = "in_person"
    blended = "blended"


class BillingPeriod(str, enum.Enum):
    once = "once"
    monthly = "monthly"
    yearly = "yearly"


class CoursePrice(Base, TimestampMixin):
    __tablename__ = "course_prices"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    course_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
    )

    delivery_type: Mapped[DeliveryType] = mapped_column(
        Enum(
            DeliveryType,
            name="delivery_type",
        ),
        nullable=False,
    )

    billing_period: Mapped[BillingPeriod] = mapped_column(
        Enum(
            BillingPeriod,
            name="billing_period",
        ),
        nullable=False,
        default=BillingPeriod.once,
    )

    list_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    sale_price: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="EUR",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    course: Mapped["Course"] = relationship(
        "Course",
        back_populates="prices",
    )
