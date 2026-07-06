from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.models.user import SystemRole
from app.services.user_auth0_service import Auth0Service
from app.services.user_service import UserService

from tests.e2e.helpers.auth0 import get_access_token

DISPOSABLE_PASSWORD = "Test-Password-123!"


def create_e2e_user(
    client: TestClient,
    *,
    role: SystemRole = SystemRole.user,
):
    """Create a real Auth0 user and provision the local database user."""

    auth0 = Auth0Service()

    email = f"e2e-{uuid.uuid4().hex[:12]}@example.com"
    name = "E2E Test User"

    auth0_user = auth0.create_user(
        email=email,
        password=DISPOSABLE_PASSWORD,
        name=name,
    )

    access_token = get_access_token(email, DISPOSABLE_PASSWORD)

    # Trigger lazy provisioning
    response = client.get(
        "/users/current",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )
    response.raise_for_status()

    session = SessionLocal()

    try:
        service = UserService(session)

        user = service.get_by_auth0_id(auth0_user.auth0_id)

        if user is None:
            raise RuntimeError("Failed to provision local user.")

        # Use the service layer instead of mutating directly.
        service.set_role(user.id, role)

        session.commit()
        session.refresh(user)

        user_id = user.id

    finally:
        session.close()

    def cleanup():
        auth0.delete_user(auth0_user.auth0_id)

        session = SessionLocal()

        try:
            service = UserService(session)

            user = service.get_by_auth0_id(auth0_user.auth0_id)

            if user:
                service.permanently_delete_user(user.id)
                session.commit()

        finally:
            session.close()

    return {
        "auth0_id": auth0_user.auth0_id,
        "user_id": user_id,
        "email": email,
        "password": DISPOSABLE_PASSWORD,
        "name": name,
        "access_token": access_token,
        "role": role,
        "cleanup": cleanup,
    }