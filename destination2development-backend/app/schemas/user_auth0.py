from __future__ import annotations

from pydantic import BaseModel, EmailStr


class Auth0User(BaseModel):
    auth0_id: str
    email: EmailStr
    name: str | None = None