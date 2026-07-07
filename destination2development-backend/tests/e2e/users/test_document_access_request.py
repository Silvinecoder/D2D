from __future__ import annotations


def test_create_document_access_request(
    client,
    disposable_user,
):
    response = client.post(
        "/document-access-requests",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
        json={
            "reason": "I need access to upload my documents.",
        },
    )

    assert response.status_code == 200

    request = response.json()

    assert request["user_id"] == str(disposable_user["user_id"])
    assert request["reason"] == "I need access to upload my documents."
    assert request["status"] == "pending"


def test_user_cannot_create_duplicate_pending_request(
    client,
    disposable_user,
):
    payload = {
        "reason": "Need document access.",
    }

    first = client.post(
        "/document-access-requests",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
        json=payload,
    )

    assert first.status_code == 200

    second = client.post(
        "/document-access-requests",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
        json=payload,
    )

    assert second.status_code == 409
    assert second.json()["detail"] == "Pending access request already exists."


def test_user_can_view_own_access_request(
    client,
    disposable_user,
):
    create = client.post(
        "/document-access-requests",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
        json={
            "reason": "Need review.",
        },
    )

    request_id = create.json()["id"]

    response = client.get(
        f"/document-access-requests/{request_id}",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
    )

    assert response.status_code == 200

    request = response.json()

    assert request["id"] == request_id


def test_admin_can_list_access_requests(
    client,
    admin_user,
    disposable_user,
):
    client.post(
        "/document-access-requests",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
        json={
            "reason": "Waiting for approval.",
        },
    )

    response = client.get(
        "/document-access-requests/admin",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    assert response.status_code == 200

    requests = response.json()

    assert any(
        request["user_id"] == str(disposable_user["user_id"]) for request in requests
    )


def test_admin_can_approve_request(
    client,
    admin_user,
    disposable_user,
):
    create = client.post(
        "/document-access-requests",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
        json={
            "reason": "Approve this request.",
        },
    )

    request_id = create.json()["id"]

    response = client.patch(
        f"/document-access-requests/admin/{request_id}/approve",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    assert response.status_code == 200

    request = response.json()

    assert request["status"] == "approved"
    assert request["reviewed_by"] == str(admin_user["user_id"])


def test_admin_can_reject_request(
    client,
    admin_user,
    disposable_user,
):
    create = client.post(
        "/document-access-requests",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
        json={
            "reason": "Reject this request.",
        },
    )

    request_id = create.json()["id"]

    response = client.patch(
        f"/document-access-requests/admin/{request_id}/reject",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    assert response.status_code == 200

    request = response.json()

    assert request["status"] == "rejected"
    assert request["reviewed_by"] == str(admin_user["user_id"])


def test_admin_cannot_process_same_request_twice(
    client,
    admin_user,
    disposable_user,
):
    create = client.post(
        "/document-access-requests",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
        json={
            "reason": "Process once.",
        },
    )

    request_id = create.json()["id"]

    response = client.patch(
        f"/document-access-requests/admin/{request_id}/approve",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    assert response.status_code == 200

    response = client.patch(
        f"/document-access-requests/admin/{request_id}/reject",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Request already processed."


def test_regular_user_cannot_list_all_access_requests(
    client,
    disposable_user,
):
    response = client.get(
        "/document-access-requests/admin",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
    )

    assert response.status_code in (401, 403)
