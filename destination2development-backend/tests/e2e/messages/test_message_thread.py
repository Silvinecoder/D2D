from __future__ import annotations


def test_create_message_thread(
    client,
    student_user,
):
    response = client.post(
        "/message-threads",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
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
    assert thread["created_by"] == str(student_user["user_id"])


def test_list_message_threads(
    client,
    student_user,
):
    client.post(
        "/message-threads",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
        },
        json={
            "message_type": "chat",
            "subject": "Thread",
        },
    )

    response = client.get(
        "/message-threads",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
        },
    )

    assert response.status_code == 200

    threads = response.json()

    assert len(threads) >= 1
