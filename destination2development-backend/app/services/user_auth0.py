from __future__ import annotations

import urllib.parse

import httpx

from app.core.config import settings
from app.schemas.user_auth0 import Auth0User


class Auth0Service:
    def __init__(self):
        self.base_url = f"https://{settings.AUTH0_DOMAIN}"

    def _send(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        json: dict | None = None,
    ) -> dict:
        with httpx.Client(timeout=10) as client:
            response = client.request(
                method,
                url,
                headers=headers,
                json=json,
            )

        response.raise_for_status()

        return response.json() if response.content else {}

    def _management_request(
        self,
        method: str,
        path: str,
        *,
        json: dict | None = None,
    ) -> dict:
        return self._send(
            method,
            f"{self.base_url}{path}",
            headers={
                "Authorization": f"Bearer {self.get_management_token()}",
            },
            json=json,
        )

    @staticmethod
    def _user_path(auth0_id: str) -> str:
        encoded = urllib.parse.quote(
            auth0_id,
            safe="",
        )

        return f"/api/v2/users/{encoded}"

    @staticmethod
    def _build_user(
        data: dict,
        *,
        id_field: str,
    ) -> Auth0User:
        return Auth0User(
            auth0_id=data[id_field],
            email=data["email"],
            name=data.get("name"),
        )

    def get_management_token(self) -> str:
        data = self._send(
            "POST",
            f"{self.base_url}/oauth/token",
            json={
                "grant_type": settings.AUTH0_GRANT_TYPE,
                "client_id": settings.AUTH0_CLIENT_ID,
                "client_secret": settings.AUTH0_CLIENT_SECRET,
                "audience": settings.AUTH0_MANAGEMENT_AUDIENCE,
            },
        )

        return data["access_token"]

    def get_user(
        self,
        access_token: str,
    ) -> Auth0User:
        data = self._send(
            "GET",
            f"{self.base_url}/userinfo",
            headers={
                "Authorization": f"Bearer {access_token}",
            },
        )

        return self._build_user(
            data,
            id_field="sub",
        )

    def create_user(
        self,
        email: str,
        password: str,
        name: str,
    ) -> Auth0User:
        data = self._management_request(
            "POST",
            "/api/v2/users",
            json={
                "connection": "Username-Password-Authentication",
                "email": email,
                "password": password,
                "name": name,
            },
        )

        return self._build_user(
            data,
            id_field="user_id",
        )

    def update_user(
        self,
        auth0_id: str,
        **changes,
    ) -> None:
        self._management_request(
            "PATCH",
            self._user_path(auth0_id),
            json=changes,
        )

    def update_email(
        self,
        auth0_id: str,
        email: str,
    ) -> None:
        self.update_user(
            auth0_id,
            email=email,
        )

    def update_password(
        self,
        auth0_id: str,
        password: str,
    ) -> None:
        self.update_user(
            auth0_id,
            password=password,
            connection="Username-Password-Authentication",
        )

    def update_name(
        self,
        auth0_id: str,
        name: str,
    ) -> None:
        self.update_user(
            auth0_id,
            name=name,
        )

    def delete_user(
        self,
        auth0_id: str,
    ) -> None:
        self._management_request(
            "DELETE",
            self._user_path(auth0_id),
        )
