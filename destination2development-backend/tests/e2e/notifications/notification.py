from __future__ import annotations


def test_create_notification(
    client,
    disposable_user,
):
    response = client.post(
        "/notifications",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
        json={
            "event_type": "message_sent",
            "entity_type": "message",
            "entity_id": str(disposable_user["user_id"]),
            "title": "New message",
            "body": "You have received a new message.",
        },
    )

    assert response.status_code == 200

    notification = response.json()

    assert notification["user_id"] == str(disposable_user["user_id"])
    assert notification["event_type"] == "message_sent"
    assert notification["entity_type"] == "message"
    assert notification["title"] == "New message"
    assert notification["body"] == "You have received a new message."
    assert notification["read_at"] is None


def test_list_notifications(
    client,
    disposable_user,
):
    client.post(
        "/notifications",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
        json={
            "event_type": "message_sent",
            "entity_type": "message",
            "entity_id": str(disposable_user["user_id"]),
            "title": "Notification",
            "body": "Test notification",
        },
    )

    response = client.get(
        "/notifications",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
    )

    assert response.status_code == 200

    notifications = response.json()

    assert len(notifications) >= 1

    notification = notifications[0]

    assert notification["title"] == "Notification"
    assert notification["body"] == "Test notification"


def test_mark_notification_as_read(
    client,
    disposable_user,
):
    notification = client.post(
        "/notifications",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
        json={
            "event_type": "message_sent",
            "entity_type": "message",
            "entity_id": str(disposable_user["user_id"]),
            "title": "Notification",
            "body": "Test notification",
        },
    ).json()

    response = client.patch(
        f"/notifications/{notification['id']}/read",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
    )

    assert response.status_code == 200

    notification = response.json()

    assert notification["read_at"] is not None
