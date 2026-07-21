from __future__ import annotations


def test_add_participant(
    client,
    student_user,
):
    thread = client.post(
        "/message-threads",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
        },
        json={
            "message_type": "chat",
        },
    ).json()

    response = client.post(
        "/message-thread-participants",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
        },
        json={
            "thread_id": thread["id"],
            "user_id": str(student_user["user_id"]),
        },
    )

    assert response.status_code == 200

    participant = response.json()

    assert participant["thread_id"] == thread["id"]
    assert participant["user_id"] == str(student_user["user_id"])


def test_list_participants(
    client,
    student_user,
):
    thread = client.post(
        "/message-threads",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
        },
        json={
            "message_type": "chat",
        },
    ).json()

    client.post(
        "/message-thread-participants",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
        },
        json={
            "thread_id": thread["id"],
            "user_id": str(student_user["user_id"]),
        },
    )

    response = client.get(
        f"/message-thread-participants/{thread['id']}",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
        },
    )

    assert response.status_code == 200

    participants = response.json()

    assert len(participants) == 1
    assert participants[0]["user_id"] == str(student_user["user_id"])


def test_remove_participant(
    client,
    student_user,
):
    thread = client.post(
        "/message-threads",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
        },
        json={
            "message_type": "chat",
        },
    ).json()

    client.post(
        "/message-thread-participants",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
        },
        json={
            "thread_id": thread["id"],
            "user_id": str(student_user["user_id"]),
        },
    )

    response = client.request(
        "DELETE",
        "/message-thread-participants",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
        },
        json={
            "thread_id": thread["id"],
            "user_id": str(student_user["user_id"]),
        },
    )

    assert response.status_code == 204

    response = client.get(
        f"/message-thread-participants/{thread['id']}",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
        },
    )

    assert response.json() == []


def test_student_can_message_assessor(
    client,
    student_user,
    assessor_user,
):
    thread_response = client.post(
        "/message-threads",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
        },
        json={
            "message_type": "chat",
        },
    )

    assert thread_response.status_code == 200

    thread = thread_response.json()

    student_response = client.post(
        "/message-thread-participants",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
        },
        json={
            "thread_id": thread["id"],
            "user_id": str(student_user["user_id"]),
        },
    )

    assert student_response.status_code == 200

    assessor_response = client.post(
        "/message-thread-participants",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
        },
        json={
            "thread_id": thread["id"],
            "user_id": str(assessor_user["user_id"]),
        },
    )

    assert assessor_response.status_code == 200

    response = client.get(
        f"/message-thread-participants/{thread['id']}",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
        },
    )

    assert response.status_code == 200

    participants = response.json()

    assert len(participants) == 2

    participant_ids = {participant["user_id"] for participant in participants}

    assert str(student_user["user_id"]) in participant_ids
    assert str(assessor_user["user_id"]) in participant_ids
