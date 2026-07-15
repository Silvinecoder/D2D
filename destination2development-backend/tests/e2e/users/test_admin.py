from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.core.database import SessionLocal
from app.services.user import UserService


def test_get_all_users_admin(client, admin_user):
    response = client.get(
        "/users/admin",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    assert response.status_code == 200

    users = response.json()

    assert isinstance(users, list)
    assert any(user["email"] == admin_user["email"] for user in users)


def test_get_user_admin(client, admin_user, disposable_user):
    target_user_id = disposable_user["user_id"]

    response = client.get(
        f"/users/admin/{target_user_id}",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    assert response.status_code == 200

    user = response.json()

    assert user["id"] == str(target_user_id)
    assert user["email"] == disposable_user["email"]


def test_update_user_role_admin(client, admin_user, disposable_user):
    target_user_id = disposable_user["user_id"]

    response = client.patch(
        f"/users/admin/{target_user_id}/role",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
        json={
            "system_role": "admin",
        },
    )

    assert response.status_code == 200

    user = response.json()

    assert user["system_role"] == "admin"


def test_lock_user_admin(client, admin_user, disposable_user):
    target_user_id = disposable_user["user_id"]

    response = client.patch(
        f"/users/admin/{target_user_id}/lock",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    assert response.status_code == 200

    user = response.json()

    assert user["account_status"] == "locked"


def test_deactivate_user_admin(client, admin_user, disposable_user):
    target_user_id = disposable_user["user_id"]

    response = client.patch(
        f"/users/admin/{target_user_id}/deactivate",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    assert response.status_code == 200

    user = response.json()

    assert user["deactivated_at"] is not None
    assert user["scheduled_deletion_at"] is not None


def test_restore_user_admin(client, admin_user, disposable_user):
    target_user_id = disposable_user["user_id"]

    # First deactivate the user.
    response = client.patch(
        f"/users/admin/{target_user_id}/deactivate",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    assert response.status_code == 200

    # Then restore.
    response = client.patch(
        f"/users/admin/{target_user_id}/restore",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    assert response.status_code == 200

    user = response.json()

    assert user["account_status"] == "active"
    assert user["deactivated_at"] is None
    assert user["scheduled_deletion_at"] is None


def test_process_scheduled_deletions_admin(client, admin_user, disposable_user):
    target_user_id = disposable_user["user_id"]

    # Schedule deletion via the API.
    response = client.patch(
        f"/users/admin/{target_user_id}/deactivate",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    assert response.status_code == 200

    # Move the scheduled deletion into the past so it becomes eligible.
    session = SessionLocal()

    try:
        service = UserService(session)

        user = service.get_by_id(target_user_id)

        user.scheduled_deletion_at = datetime.now(UTC) - timedelta(minutes=1)

        session.commit()

    finally:
        session.close()

    response = client.post(
        "/users/admin/process-deletions",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    assert response.status_code == 200

    deleted = response.json()

    assert any(user["id"] == str(target_user_id) for user in deleted)

    response = client.get(
        f"/users/admin/{target_user_id}",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    assert response.status_code == 404


def test_admin_forbidden_for_regular_user(client, disposable_user):
    response = client.get(
        "/users/admin",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
    )

    assert response.status_code in (401, 403)
