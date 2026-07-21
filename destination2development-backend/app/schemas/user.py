from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models.user import (
    AccountStatus,
    SystemRole,
    AccountType,
)


class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    name: str
    account_status: AccountStatus
    system_role: SystemRole
    account_type: AccountType | None = None
    last_login_at: datetime | None = None
    deactivated_at: datetime | None = None

    model_config = {
        "from_attributes": True,
    }


class UserAccountTypeUpdate(BaseModel):
    account_type: AccountType


class UserNameUpdate(BaseModel):
    name: str


class UserEmailUpdate(BaseModel):
    email: EmailStr


class UserPasswordUpdate(BaseModel):
    password: str


class UserRoleUpdate(BaseModel):
    system_role: SystemRole
