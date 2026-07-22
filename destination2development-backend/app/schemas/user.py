from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, model_validator

from app.models.user import (
    AccountStatus,
    SystemRole,
    AccountType,
)
from app.models.business import BusinessRole


class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    name: str
    account_status: AccountStatus
    system_role: SystemRole
    account_type: AccountType | None = None
    business_id: uuid.UUID | None = None
    business_role: BusinessRole | None = None
    last_login_at: datetime | None = None
    deactivated_at: datetime | None = None

    model_config = {
        "from_attributes": True,
    }


class UserAccountTypeUpdate(BaseModel):
    """Self-service account type update — student/assessor only.
    Business accounts are assigned separately via the admin business-assignment endpoint,
    since they require a real business_id and role to attach to.
    """
    account_type: AccountType


class UserBusinessAssignmentUpdate(BaseModel):
    """Admin-only: assign a user to a business with a role."""
    business_id: uuid.UUID
    business_role: BusinessRole


class UserBusinessRoleUpdate(BaseModel):
    """Admin-only: change an existing business user's role."""
    business_role: BusinessRole


class UserNameUpdate(BaseModel):
    name: str


class UserEmailUpdate(BaseModel):
    email: EmailStr


class UserPasswordUpdate(BaseModel):
    password: str


class UserRoleUpdate(BaseModel):
    system_role: SystemRole