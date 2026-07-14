from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.assistant.model_helper import Base, TimestampMixin

if TYPE_CHECKING:
    from .user import User


class DocumentType(str, enum.Enum):
    agreement = "agreement"
    dbs = "dbs"
    passport = "identification"
    qualification = "qualification"
    profile_photo = "profile_photo"


class VerificationStatus(str, enum.Enum):
    pending = "pending"
    in_review = "in_review"
    approved = "approved"
    rejected = "rejected"
    requires_action = "requires_action"


class ProfileDocument(Base, TimestampMixin):
    __tablename__ = "profile_documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    document_type: Mapped[DocumentType] = mapped_column(
        Enum(DocumentType, name="document_type"),
        nullable=False,
    )

    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    verification_status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus, name="verification_status"),
        default=VerificationStatus.pending,
        nullable=False,
    )

    verified_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user: Mapped[User] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="profile_documents",
    )

    verifier: Mapped[User | None] = relationship(
        "User",
        foreign_keys=[verified_by],
        back_populates="verified_documents",
    )
