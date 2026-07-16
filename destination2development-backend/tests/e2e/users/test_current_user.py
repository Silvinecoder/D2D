from __future__ import annotations

import httpx

from app.core.config import settings

from tests.e2e.helpers.auth0 import get_access_token


def test_get_current_user(client, disposable_user):
    access_token = disposable_user["access_token"]

    response = client.get(
        "/users/current",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert response.status_code == 200

    user = response.json()

    assert user["email"] == disposable_user["email"]
    assert user["system_role"] == "user"
    assert user["account_status"] == "active"


def test_update_current_user_name(client, disposable_user):
    access_token = disposable_user["access_token"]

    response = client.patch(
        "/users/current/name",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
        json={
            "name": "Jason",
        },
    )

    assert response.status_code == 200

    response = client.get(
        "/users/current",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    user = response.json()

    assert user["name"] == "Jason"


def test_create_new_user(client, disposable_user):
    access_token = disposable_user["access_token"]

    response = client.get(
        "/users/current",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert response.status_code == 200

    user = response.json()

    assert user["email"] == disposable_user["email"]
    assert user["name"] == disposable_user["name"]
    assert user["system_role"] == "user"
    assert user["account_status"] == "active"
    assert user["last_login_at"] is not None


def test_update_current_user_password(client, disposable_user):
    access_token = disposable_user["access_token"]

    new_password = "New-Test-Password-456!"

    response = client.patch(
        "/users/current/password",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
        json={
            "password": new_password,
        },
    )

    assert response.status_code == 200

    old_login = httpx.post(
        f"https://{settings.AUTH0_DOMAIN}/oauth/token",
        json={
            "grant_type": settings.AUTH0_PASSWORD_GRANT_TYPE,
            "username": disposable_user["email"],
            "password": disposable_user["password"],
            "realm": "Username-Password-Authentication",
            "audience": settings.AUTH0_AUDIENCE,
            "client_id": settings.AUTH0_CLIENT_ID,
            "client_secret": settings.AUTH0_CLIENT_SECRET,
            "scope": "openid profile email",
        },
        timeout=10,
    )

    assert old_login.status_code != 200

    new_access_token = get_access_token(
        disposable_user["email"],
        new_password,
    )

    assert new_access_token


def test_update_current_user_email(client, disposable_user):
    access_token = disposable_user["access_token"]

    new_email = f"updated-{disposable_user['auth0_id'][-12:]}@example.com"

    response = client.patch(
        "/users/current/email",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
        json={
            "email": new_email,
        },
    )

    assert response.status_code == 200

    user = response.json()

    assert user["email"] == new_email

    response = client.get(
        "/users/current",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert response.json()["email"] == new_email

    new_login_token = get_access_token(
        new_email,
        disposable_user["password"],
    )

    assert new_login_token


def test_delete_current_user(client, disposable_user):
    access_token = disposable_user["access_token"]

    response = client.delete(
        "/users/current",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert response.status_code == 200

    user = response.json()

    assert user["account_status"] == "deactivated"
    assert user["deactivated_at"] is not None

    response = client.get(
        "/users/current",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert response.status_code == 200
