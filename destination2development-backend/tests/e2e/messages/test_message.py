from __future__ import annotations


def test_student_and_assessor_can_exchange_messages(
    client,
    student_user,
    assessor_user,
):
    # Student creates the conversation
    thread_response = client.post(
        "/message-threads",
        headers={
            "Authorization": f"Bearer{student_user['access_token']}",
        },
        json={
            "message_type": "chat",
        },
    )

    assert thread_response.status_code == 200

    thread = thread_response.json()

    # Add student as participant
    student_participant = client.post(
        "/message-thread-participants",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
        },
        json={
            "thread_id": thread["id"],
            "user_id": str(student_user["user_id"]),
        },
    )

    assert student_participant.status_code == 200

    # Add assessor as participant
    assessor_participant = client.post(
        "/message-thread-participants",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
        },
        json={
            "thread_id": thread["id"],
            "user_id": str(assessor_user["user_id"]),
        },
    )

    assert assessor_participant.status_code == 200

    # Student sends first message
    student_message = client.post(
        f"/message-threads/{thread['id']}/messages",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
        },
        json={
            "body": "Hello, I need help with this course.",
        },
    )

    assert student_message.status_code == 200

    student_message_data = student_message.json()

    assert student_message_data["body"] == "Hello, I need help with this course."
    assert student_message_data["sender_id"] == str(student_user["user_id"])

    # Assessor replies
    assessor_message = client.post(
        f"/message-threads/{thread['id']}/messages",
        headers={
            "Authorization": f"Bearer {assessor_user['access_token']}",
        },
        json={
            "body": "Hi, I can help you with your course questions.",
        },
    )

    assert assessor_message.status_code == 200

    assessor_message_data = assessor_message.json()

    assert (
        assessor_message_data["body"]
        == "Hi, I can help you with your course questions."
    )
    assert assessor_message_data["sender_id"] == str(assessor_user["user_id"])

    # Both messages are visible in the thread
    response = client.get(
        f"/message-threads/{thread['id']}/messages",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
        },
    )

    assert response.status_code == 200

    messages = response.json()

    assert len(messages) == 2

    assert messages[0]["sender_id"] == str(student_user["user_id"])
    assert messages[0]["body"] == "Hello, I need help with this course."

    assert messages[1]["sender_id"] == str(assessor_user["user_id"])
    assert messages[1]["body"] == "Hi, I can help you with your course questions."
