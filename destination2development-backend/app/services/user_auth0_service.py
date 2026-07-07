from __future__ import annotations

import httpx

from app.core.config import settings
from app.schemas.user_auth0 import Auth0User


class Auth0Service:
    def get_management_token(
        self,
    ) -> str:

        with httpx.Client(timeout=10) as client:
            response = client.post(
                f"https://{settings.AUTH0_DOMAIN}/oauth/token",
                json={
                    "grant_type": settings.AUTH0_GRANT_TYPE,
                    "client_id": settings.AUTH0_CLIENT_ID,
                    "client_secret": settings.AUTH0_CLIENT_SECRET,
                    "audience": settings.AUTH0_MANAGEMENT_AUDIENCE,
                },
            )

        print(response.status_code)
        print(response.text)

        response.raise_for_status()

        return response.json()["access_token"]

    def _management_headers(
        self,
    ) -> dict[str, str]:

        return {
            "Authorization": f"Bearer {self.get_management_token()}",
        }

    def get_user(
        self,
        access_token: str,
    ) -> Auth0User:

        with httpx.Client(timeout=10) as client:
            response = client.get(
                f"https://{settings.AUTH0_DOMAIN}/userinfo",
                headers={
                    "Authorization": f"Bearer {access_token}",
                },
            )

        response.raise_for_status()

        data = response.json()

        return Auth0User(
            auth0_id=data["sub"],
            email=data["email"],
            name=data.get("name"),
        )

    def create_user(
        self,
        email: str,
        password: str,
        name: str,
    ) -> Auth0User:

        with httpx.Client(timeout=10) as client:
            response = client.post(
                f"https://{settings.AUTH0_DOMAIN}/api/v2/users",
                headers=self._management_headers(),
                json={
                    "connection": "Username-Password-Authentication",
                    "email": email,
                    "password": password,
                    "name": name,
                },
            )

        response.raise_for_status()

        data = response.json()

        return Auth0User(
            auth0_id=data["user_id"],
            email=data["email"],
            name=data.get("name"),
        )

    def update_email(
        self,
        auth0_id: str,
        email: str,
    ):

        with httpx.Client(timeout=10) as client:
            response = client.patch(
                f"https://{settings.AUTH0_DOMAIN}/api/v2/users/{auth0_id}",
                headers=self._management_headers(),
                json={
                    "email": email,
                },
            )

        response.raise_for_status()

    def update_password(
        self,
        auth0_id: str,
        password: str,
    ):

        with httpx.Client(timeout=10) as client:
            response = client.patch(
                f"https://{settings.AUTH0_DOMAIN}/api/v2/users/{auth0_id}",
                headers=self._management_headers(),
                json={
                    "password": password,
                    "connection": "Username-Password-Authentication",
                },
            )

        response.raise_for_status()

    def update_name(
        self,
        auth0_id: str,
        name: str,
    ):

        with httpx.Client(timeout=10) as client:
            response = client.patch(
                f"https://{settings.AUTH0_DOMAIN}/api/v2/users/{auth0_id}",
                headers=self._management_headers(),
                json={
                    "name": name,
                },
            )

        response.raise_for_status()

    def delete_user(
        self,
        auth0_id: str,
    ):

        with httpx.Client(timeout=10) as client:
            response = client.delete(
                f"https://{settings.AUTH0_DOMAIN}/api/v2/users/{auth0_id}",
                headers=self._management_headers(),
            )

        response.raise_for_status()
