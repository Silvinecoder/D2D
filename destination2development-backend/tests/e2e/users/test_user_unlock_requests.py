from __future__ import annotations


def test_create_unlock_request(client, admin_user, disposable_user):
    response = client.patch(
        f"/users/admin/{disposable_user['user_id']}/lock",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    assert response.status_code == 200

    response = client.post(
        "/unlock-requests",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
        json={
            "message": "Please unlock my account.",
        },
    )

    assert response.status_code == 200

    request = response.json()

    assert request["user_id"] == str(disposable_user["user_id"])
    assert request["message"] == "Please unlock my account."
    assert request["status"] == "pending"


def test_create_unlock_request_returns_existing_pending_request(
    client,
    admin_user,
    disposable_user,
):
    response = client.patch(
        f"/users/admin/{disposable_user['user_id']}/lock",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    assert response.status_code == 200

    first = client.post(
        "/unlock-requests",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
        json={
            "message": "First request",
        },
    )

    second = client.post(
        "/unlock-requests",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
        json={
            "message": "Second request",
        },
    )

    assert first.status_code == 200
    assert second.status_code == 200

    assert first.json()["id"] == second.json()["id"]
    assert second.json()["status"] == "pending"


def test_list_unlock_requests_admin(
    client,
    admin_user,
    disposable_user,
):
    response = client.patch(
        f"/users/admin/{disposable_user['user_id']}/lock",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    assert response.status_code == 200

    response = client.post(
        "/unlock-requests",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
        json={
            "message": "Please unlock me.",
        },
    )

    assert response.status_code == 200

    response = client.get(
        "/unlock-requests/admin",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    assert response.status_code == 200

    requests = response.json()

    assert isinstance(requests, list)

    assert any(
        request["user_id"] == str(disposable_user["user_id"]) for request in requests
    )


def test_approve_unlock_request(
    client,
    admin_user,
    disposable_user,
):
    response = client.patch(
        f"/users/admin/{disposable_user['user_id']}/lock",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    assert response.status_code == 200

    response = client.post(
        "/unlock-requests",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
        json={
            "message": "Please unlock me.",
        },
    )

    assert response.status_code == 200

    request_id = response.json()["id"]

    response = client.patch(
        f"/unlock-requests/admin/{request_id}/approve",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    assert response.status_code == 200

    request = response.json()

    assert request["status"] == "approved"

    response = client.get(
        f"/users/admin/{disposable_user['user_id']}",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    assert response.status_code == 200

    user = response.json()

    assert user["account_status"] == "active"


def test_reject_unlock_request(
    client,
    admin_user,
    disposable_user,
):
    response = client.patch(
        f"/users/admin/{disposable_user['user_id']}/lock",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    assert response.status_code == 200

    response = client.post(
        "/unlock-requests",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
        json={
            "message": "Please unlock me.",
        },
    )

    assert response.status_code == 200

    request_id = response.json()["id"]

    response = client.patch(
        f"/unlock-requests/admin/{request_id}/reject",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    assert response.status_code == 200

    request = response.json()

    assert request["status"] == "rejected"


def test_unlock_request_admin_forbidden_for_regular_user(
    client,
    disposable_user,
):
    response = client.get(
        "/unlock-requests/admin",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
    )

    assert response.status_code in (401, 403)


def test_create_unlock_request_conflict_if_not_locked(client, disposable_user):
    response = client.post(
        "/unlock-requests",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
        json={
            "message": "Please unlock my account.",
        },
    )

    assert response.status_code == 409


def test_approve_unlock_request_conflict_if_already_approved(
    client,
    admin_user,
    disposable_user,
):
    response = client.patch(
        f"/users/admin/{disposable_user['user_id']}/lock",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    assert response.status_code == 200

    response = client.post(
        "/unlock-requests",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
        json={
            "message": "Please unlock me.",
        },
    )

    assert response.status_code == 200

    request_id = response.json()["id"]

    # First approval succeeds and reactivates the account.
    response = client.patch(
        f"/unlock-requests/admin/{request_id}/approve",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    assert response.status_code == 200

    # Approving the same (now-stale) request again should fail: the
    # account is no longer locked.
    response = client.patch(
        f"/unlock-requests/admin/{request_id}/approve",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    assert response.status_code == 409