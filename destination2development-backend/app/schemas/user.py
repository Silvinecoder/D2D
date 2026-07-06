from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models.user import (
    AccountStatus,
    SystemRole,
)


class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    name: str

    account_status: AccountStatus
    system_role: SystemRole

    last_login_at: datetime | None

    deactivated_at: datetime |None
    scheduled_deletion_at: datetime | None
    deleted_at: datetime | None

    model_config = {
        "from_attributes": True,
    }


class UserNameUpdate(BaseModel):
    name: str


class UserEmailUpdate(BaseModel):
    email: EmailStr


class UserPasswordUpdate(BaseModel):
    password: str


class UserRoleUpdate(BaseModel):
    system_role: SystemRole