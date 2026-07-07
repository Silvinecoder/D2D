from __future__ import annotations

import httpx

from app.core.config import settings


def get_access_token(username: str, password: str) -> str:
    response = httpx.post(
        f"https://{settings.AUTH0_DOMAIN}/oauth/token",
        json={
            "grant_type": settings.AUTH0_PASSWORD_GRANT_TYPE,
            "username": username,
            "password": password,
            "realm": "Username-Password-Authentication",
            "audience": settings.AUTH0_AUDIENCE,
            "client_id": settings.AUTH0_CLIENT_ID,
            "client_secret": settings.AUTH0_CLIENT_SECRET,
            "scope": "openid profile email",
        },
        timeout=10,
    )
    response.raise_for_status()

    return response.json()["access_token"]
