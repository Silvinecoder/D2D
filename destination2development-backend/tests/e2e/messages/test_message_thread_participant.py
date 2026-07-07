from __future__ import annotations


def test_add_participant(
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
        "/message-thread-participants",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
        json={
            "thread_id": thread["id"],
            "user_id": str(disposable_user["user_id"]),
            "role": "student",
        },
    )

    assert response.status_code == 200

    participant = response.json()

    assert participant["thread_id"] == thread["id"]
    assert participant["user_id"] == str(disposable_user["user_id"])
    assert participant["role"] == "student"


def test_list_participants(
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
        "/message-thread-participants",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
        json={
            "thread_id": thread["id"],
            "user_id": str(disposable_user["user_id"]),
            "role": "student",
        },
    )

    response = client.get(
        f"/message-thread-participants/{thread['id']}",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
    )

    assert response.status_code == 200

    participants = response.json()

    assert len(participants) == 1
    assert participants[0]["user_id"] == str(disposable_user["user_id"])


def test_remove_participant(
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
        "/message-thread-participants",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
        json={
            "thread_id": thread["id"],
            "user_id": str(disposable_user["user_id"]),
            "role": "student",
        },
    )

    response = client.request(
        "DELETE",
        "/message-thread-participants",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
        json={
            "thread_id": thread["id"],
            "user_id": str(disposable_user["user_id"]),
        },
    )

    assert response.status_code == 200

    response = client.get(
        f"/message-thread-participants/{thread['id']}",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
    )

    assert response.json() == []
