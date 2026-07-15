from __future__ import annotations


def test_recipient_is_notified_when_they_receive_a_message(
    client,
    disposable_user,
    admin_user,
):
    thread = client.post(
        "/message-threads",
        headers={"Authorization": f"Bearer {disposable_user['access_token']}"},
        json={"message_type": "chat"},
    ).json()

    client.post(
        "/message-thread-participants",
        headers={"Authorization": f"Bearer {disposable_user['access_token']}"},
        json={
            "thread_id": thread["id"],
            "user_id": str(admin_user["user_id"]),
            "role": "admin",
        },
    )

    client.post(
        f"/message-threads/{thread['id']}/messages",
        headers={"Authorization": f"Bearer {disposable_user['access_token']}"},
        json={
            "body": "Hello!",
        },
    )

    response = client.get(
        "/notifications",
        headers={"Authorization": f"Bearer {admin_user['access_token']}"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["unread_count"] == 1

    assert any(
        notification["event_type"] == "message_sent" for notification in data["items"]
    )

    sender_notifications = client.get(
        "/notifications",
        headers={"Authorization": f"Bearer {disposable_user['access_token']}"},
    ).json()

    assert sender_notifications["unread_count"] == 0

    assert not any(
        notification["event_type"] == "message_sent"
        for notification in sender_notifications["items"]
    )


def test_can_mark_notification_as_read(
    client,
    disposable_user,
    admin_user,
):
    thread = client.post(
        "/message-threads",
        headers={"Authorization": f"Bearer {disposable_user['access_token']}"},
        json={"message_type": "chat"},
    ).json()

    client.post(
        "/message-thread-participants",
        headers={"Authorization": f"Bearer {disposable_user['access_token']}"},
        json={
            "thread_id": thread["id"],
            "user_id": str(admin_user["user_id"]),
            "role": "admin",
        },
    )

    client.post(
        f"/message-threads/{thread['id']}/messages",
        headers={"Authorization": f"Bearer {disposable_user['access_token']}"},
        json={
            "thread_id": thread["id"],
            "body": "Hello!",
        },
    )

    notifications = client.get(
        "/notifications",
        headers={"Authorization": f"Bearer {admin_user['access_token']}"},
    ).json()

    notification = notifications["items"][0]

    response = client.patch(
        f"/notifications/{notification['id']}/read",
        headers={"Authorization": f"Bearer {admin_user['access_token']}"},
    )

    assert response.status_code == 200

    notification = response.json()

    assert notification["read_at"] is not None

    notifications = client.get(
        "/notifications",
        headers={"Authorization": f"Bearer {admin_user['access_token']}"},
    ).json()

    assert notifications["unread_count"] == 0


def test_user_cannot_mark_another_users_notification_as_read(
    client,
    disposable_user,
    admin_user,
):
    thread = client.post(
        "/message-threads",
        headers={"Authorization": f"Bearer {disposable_user['access_token']}"},
        json={"message_type": "chat"},
    ).json()

    client.post(
        "/message-thread-participants",
        headers={"Authorization": f"Bearer {disposable_user['access_token']}"},
        json={
            "thread_id": thread["id"],
            "user_id": str(admin_user["user_id"]),
            "role": "admin",
        },
    )

    client.post(
        f"/message-threads/{thread['id']}/messages",
        headers={"Authorization": f"Bearer {disposable_user['access_token']}"},
        json={
            "thread_id": thread["id"],
            "body": "Hello!",
        },
    )

    notifications = client.get(
        "/notifications",
        headers={"Authorization": f"Bearer {admin_user['access_token']}"},
    ).json()

    notification = notifications["items"][0]

    response = client.patch(
        f"/notifications/{notification['id']}/read",
        headers={"Authorization": f"Bearer {disposable_user['access_token']}"},
    )

    assert response.status_code == 404

    admin_notifications = client.get(
        "/notifications",
        headers={"Authorization": f"Bearer {admin_user['access_token']}"},
    ).json()

    assert admin_notifications["unread_count"] == 1
    assert admin_notifications["items"][0]["read_at"] is None
