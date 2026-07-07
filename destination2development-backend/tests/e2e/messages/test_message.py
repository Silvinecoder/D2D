from __future__ import annotations


def test_send_message(
    client,
    disposable_user,
):
    thread = client.post(
        "/message-threads",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
        json={
            "message_type": "chat",
        },
    ).json()

    response = client.post(
        "/messages",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
        json={
            "thread_id": thread["id"],
            "body": "Hello world!",
        },
    )

    assert response.status_code == 200

    message = response.json()

    assert message["body"] == "Hello world!"
    assert message["sender_id"] == str(disposable_user["user_id"])
    assert message["thread_id"] == thread["id"]


def test_list_messages(
    client,
    disposable_user,
):
    thread = client.post(
        "/message-threads",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
        json={
            "message_type": "chat",
        },
    ).json()

    client.post(
        "/messages",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
        json={
            "thread_id": thread["id"],
            "body": "First message",
        },
    )

    response = client.get(
        f"/messages/{thread['id']}",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
    )

    assert response.status_code == 200

    messages = response.json()

    assert len(messages) == 1
    assert messages[0]["body"] == "First message"


def test_mark_message_as_read(
    client,
    disposable_user,
):
    thread = client.post(
        "/message-threads",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
        json={
            "message_type": "chat",
        },
    ).json()

    message = client.post(
        "/messages",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
        json={
            "thread_id": thread["id"],
            "body": "Unread",
        },
    ).json()

    response = client.patch(
        f"/messages/{message['id']}/read",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
    )

    assert response.status_code == 200
    assert response.json()["read_at"] is not None
