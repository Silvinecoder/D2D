from __future__ import annotations


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


def test_restore_user_admin(client, admin_user, disposable_user):
    target_user_id = disposable_user["user_id"]

    # User deactivates their own account first.
    response = client.delete(
        "/users/current",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
    )

    assert response.status_code == 200

    # Admin restores it.
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


def test_delete_user_admin(client, admin_user, disposable_user):
    target_user_id = disposable_user["user_id"]

    response = client.delete(
        f"/users/admin/{target_user_id}",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    assert response.status_code == 200

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


def test_admin_can_delete_own_account(client, admin_user):
    response = client.delete(
        f"/users/admin/{admin_user['user_id']}",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    assert response.status_code == 200

    # Their own token should no longer resolve to an existing user.
    response = client.get(
        "/users/current",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    assert response.status_code in (401, 404)

def test_restore_user_admin_conflict_if_not_deactivated(client, admin_user, disposable_user):
    target_user_id = disposable_user["user_id"]

    # User is active, never deactivated — restore should be rejected.
    response = client.patch(
        f"/users/admin/{target_user_id}/restore",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    assert response.status_code == 409
