from __future__ import annotations


def test_create_profile(
    client,
    student_user,
):
    response = client.post(
        "/profile",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
        },
        json={
            "qualification": "BSc Computer Science",
            "date_of_birth": "1998-05-10",
            "gender": "female",
            "city": "London",
            "education_level": "Bachelor",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["user_id"] == str(student_user["user_id"])
    assert data["qualification"] == "BSc Computer Science"
    assert data["date_of_birth"] == "1998-05-10"
    assert data["gender"] == "female"
    assert data["city"] == "London"
    assert data["education_level"] == "Bachelor"
    assert data["avatar_document_id"] is None


def test_create_profile_twice_returns_conflict(
    client,
    student_user,
):
    response = client.post(
        "/profile",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
        },
        json={},
    )

    assert response.status_code == 200

    response = client.post(
        "/profile",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
        },
        json={},
    )

    assert response.status_code == 409


def test_get_profile(
    client,
    student_user,
):
    client.post(
        "/profile",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
        },
        json={
            "city": "Manchester",
        },
    )

    response = client.get(
        "/profile",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["city"] == "Manchester"
    assert data["user_id"] == str(student_user["user_id"])


def test_update_profile(
    client,
    student_user,
):
    client.post(
        "/profile",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
        },
        json={},
    )

    response = client.patch(
        "/profile",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
        },
        json={
            "city": "Bristol",
            "education_level": "Masters",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["city"] == "Bristol"
    assert data["education_level"] == "Masters"
