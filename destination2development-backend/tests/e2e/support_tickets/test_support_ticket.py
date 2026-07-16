from __future__ import annotations


def _create_ticket(
    client,
    student_user,
    subject="Can't access my course",
):
    response = client.post(
        "/support-tickets",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
        },
        json={
            "subject": subject,
        },
    )

    assert response.status_code == 200, response.text

    return response.json()


def test_student_can_raise_a_ticket_but_not_view_the_queue(
    client,
    student_user,
):
    response = client.post(
        "/support-tickets",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
        },
        json={
            "subject": "Can't access my course",
        },
    )

    assert response.status_code == 200, response.text

    ticket = response.json()

    assert ticket["status"] == "open"
    assert ticket["assigned_admin_id"] is None
    assert ticket["thread_id"] is not None

    anon_response = client.post(
        "/support-tickets",
        json={
            "subject": "No auth",
        },
    )

    assert anon_response.status_code == 400
    assert anon_response.json()["detail"]["error"] == "invalid_request"

    queue_response = client.get(
        "/support-tickets",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
        },
    )

    assert queue_response.status_code == 403


def test_admin_sees_new_ticket_in_the_unassigned_queue(
    client,
    student_user,
    admin_user,
):
    ticket = _create_ticket(client, student_user)

    response = client.get(
        "/support-tickets",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
        params={
            "unassigned": True,
        },
    )

    assert response.status_code == 200, response.json()

    tickets = response.json()

    assert any(t["id"] == ticket["id"] for t in tickets)
    assert all(t["assigned_admin_id"] is None for t in tickets)


def test_admin_claims_ticket_and_works_it_through_to_closed(
    client,
    student_user,
    admin_user,
):
    ticket = _create_ticket(client, student_user, "Help!")

    claim_response = client.patch(
        f"/support-tickets/{ticket['id']}/claim",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    assert claim_response.status_code == 200, claim_response.json()

    claimed = claim_response.json()

    assert claimed["assigned_admin_id"] == str(admin_user["user_id"])
    assert claimed["status"] == "in_progress"

    participants = client.get(
        f"/message-thread-participants/{ticket['thread_id']}",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    ).json()

    assert any(
        p["user_id"] == str(admin_user["user_id"]) and p["role"] == "support"
        for p in participants
    )

    resolve_response = client.patch(
        f"/support-tickets/{ticket['id']}/status",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
        json={
            "status": "resolved",
        },
    )

    assert resolve_response.status_code == 200, resolve_response.json()

    resolved = resolve_response.json()

    assert resolved["status"] == "resolved"
    assert resolved["resolved_at"] is not None
    assert resolved["closed_at"] is None

    close_response = client.patch(
        f"/support-tickets/{ticket['id']}/status",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
        json={
            "status": "closed",
        },
    )

    assert close_response.status_code == 200, close_response.json()

    closed = close_response.json()

    assert closed["status"] == "closed"
    assert closed["closed_at"] is not None

    filtered = client.get(
        "/support-tickets",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
        params={
            "status": "closed",
        },
    ).json()

    assert any(t["id"] == ticket["id"] for t in filtered)
    assert all(t["status"] == "closed" for t in filtered)


def test_ticket_cannot_skip_straight_to_resolved(
    client,
    student_user,
    admin_user,
):
    ticket = _create_ticket(client, student_user)

    response = client.patch(
        f"/support-tickets/{ticket['id']}/status",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
        json={
            "status": "resolved",
        },
    )

    assert response.status_code == 409


def test_second_admin_cannot_steal_a_claimed_ticket(
    client,
    student_user,
    admin_user,
    admin_user_two,
):
    ticket = _create_ticket(client, student_user, "Help!")

    client.patch(
        f"/support-tickets/{ticket['id']}/claim",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    response = client.patch(
        f"/support-tickets/{ticket['id']}/claim",
        headers={
            "Authorization": f"Bearer {admin_user_two['access_token']}",
        },
    )

    assert response.status_code == 409


def test_admin_can_unassign_a_ticket_back_to_the_queue(
    client,
    student_user,
    admin_user,
):
    ticket = _create_ticket(client, student_user, "Help!")

    client.patch(
        f"/support-tickets/{ticket['id']}/claim",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    response = client.patch(
        f"/support-tickets/{ticket['id']}/unassign",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    assert response.status_code == 200, response.json()

    ticket = response.json()

    assert ticket["assigned_admin_id"] is None
    assert ticket["status"] == "open"


def test_students_are_blocked_from_triage_actions(
    client,
    student_user,
    admin_user,
):
    ticket = _create_ticket(client, student_user, "Help!")

    status_response = client.patch(
        f"/support-tickets/{ticket['id']}/status",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
        },
        json={
            "status": "in_progress",
        },
    )

    assert status_response.status_code == 403

    claim_response = client.patch(
        f"/support-tickets/{ticket['id']}/claim",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
        },
    )

    assert claim_response.status_code == 403

    assign_response = client.patch(
        f"/support-tickets/{ticket['id']}/assign",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
        },
        json={
            "admin_id": str(student_user["user_id"]),
        },
    )

    assert assign_response.status_code == 403

    bad_assign_response = client.patch(
        f"/support-tickets/{ticket['id']}/assign",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
        json={
            "admin_id": str(student_user["user_id"]),
        },
    )

    assert bad_assign_response.status_code == 400
