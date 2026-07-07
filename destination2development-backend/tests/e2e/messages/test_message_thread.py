from __future__ import annotations


def test_create_message_thread(
    client,
    disposable_user,
):
    response = client.post(
        "/message-threads",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
        json={
            "message_type": "chat",
            "subject": "General Chat",
        },
    )

    assert response.status_code == 200

    thread = response.json()

    assert thread["message_type"] == "chat"
    assert thread["subject"] == "General Chat"
    assert thread["created_by"] == str(disposable_user["user_id"])


def test_list_message_threads(
    client,
    disposable_user,
):
    client.post(
        "/message-threads",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
        json={
            "message_type": "chat",
            "subject": "Thread",
        },
    )

    response = client.get(
        "/message-threads",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
    )

    assert response.status_code == 200

    threads = response.json()

    assert len(threads) >= 1


def test_close_ticket(
    client,
    disposable_user,
):
    response = client.post(
        "/message-threads",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
        json={
            "message_type": "ticket",
            "subject": "Support",
        },
    )

    thread = response.json()

    response = client.patch(
        f"/message-threads/{thread['id']}/close",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
    )

    assert response.status_code == 200

    assert response.json()["status"] == "closed"
