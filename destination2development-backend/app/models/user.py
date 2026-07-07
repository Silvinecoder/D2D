from __future__ import annotations

import datetime
import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.assistant.model_helper import Base, TimestampMixin


if TYPE_CHECKING:
    from .document_access_request import DocumentAccessRequest
    from .profile import Profile
    from .profile_document import ProfileDocument
    from .user_unlock_request import UserUnlockRequest


class AccountStatus(str, enum.Enum):
    active = "active"
    locked = "locked"
    pending_verification = "pending_verification"


class SystemRole(str, enum.Enum):
    admin = "admin"
    user = "user"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    auth0_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    account_status: Mapped[AccountStatus] = mapped_column(
        Enum(AccountStatus, name="account_status"),
        default=AccountStatus.pending_verification,
        nullable=False,
    )

    system_role: Mapped[SystemRole] = mapped_column(
        Enum(SystemRole, name="system_role"),
        default=SystemRole.user,
        nullable=False,
    )

    last_login_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    deactivated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    scheduled_deletion_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    deleted_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    profile: Mapped["Profile | None"] = relationship(
        "Profile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        single_parent=True,
    )

    profile_documents: Mapped[list["ProfileDocument"]] = relationship(
        "ProfileDocument",
        back_populates="user",
        foreign_keys="ProfileDocument.user_id",
        cascade="all, delete-orphan",
    )

    verified_documents: Mapped[list[ProfileDocument]] = relationship(
        "ProfileDocument",
        back_populates="verifier",
        foreign_keys="ProfileDocument.verified_by",
    )

    document_access_requests: Mapped[list[DocumentAccessRequest]] = relationship(
        "DocumentAccessRequest",
        back_populates="user",
        foreign_keys="DocumentAccessRequest.user_id",
        cascade="all, delete-orphan",
        single_parent=True,
    )

    reviewed_access_requests: Mapped[list[DocumentAccessRequest]] = relationship(
        "DocumentAccessRequest",
        back_populates="reviewer",
        foreign_keys="DocumentAccessRequest.reviewed_by",
    )

    unlock_requests: Mapped[list[UserUnlockRequest]] = relationship(
        "UserUnlockRequest",
        back_populates="user",
        cascade="all, delete-orphan",
    )
