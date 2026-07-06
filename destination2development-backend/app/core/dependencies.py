from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi_plugin import Auth0FastAPI
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.user import SystemRole, User
from app.services.user_auth0_service import Auth0Service
from app.services.user_service import UserService

auth0 = Auth0FastAPI(
    domain=settings.AUTH0_DOMAIN,
    audience=settings.AUTH0_AUDIENCE,
)
auth0_management = Auth0Service()
bearer_scheme = HTTPBearer()


@dataclass
class CurrentIdentity:
    auth0_id: str
    access_token: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_identity(
    claims: dict[str, Any] = Depends(auth0.require_auth()),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> CurrentIdentity:
    return CurrentIdentity(
        auth0_id=claims["sub"],
        access_token=credentials.credentials,
    )


def get_current_user(
    identity: CurrentIdentity = Depends(get_current_identity),
    session: Session = Depends(get_db),
) -> User:
    """Resolve (and lazily create) the local User row for the caller.

    This is the ONE place that does auth0.get_user -> get_or_create_auth0_user.
    Every route that needs "the calling user" should depend on this instead
    of re-implementing the lookup, which is what let the unlock-requests
    router drift out of sync with UserService's real signature.
    """
    auth0_user = auth0_management.get_user(identity.access_token)

    service = UserService(session)
    return service.get_or_create_auth0_user(auth0_user)


def get_current_active_user(
    user: User = Depends(get_current_user),
) -> User:
    """Like get_current_user, but blocks locked accounts.

    Use for endpoints a locked user shouldn't be able to use (changing
    name/email/password). Deliberately NOT used for GET /current or for
    creating an unlock request, since a locked user still needs to see
    their own status and needs to be able to ask for an unlock.
    """
    if user.account_status.value == "locked":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is locked. Submit an unlock request.",
        )
    return user


def require_admin(
    user: User = Depends(get_current_user),
) -> User:
    if user.system_role != SystemRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required.",
        )
    return user