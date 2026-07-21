from __future__ import annotations


def test_add_profile_language(
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

    languages = client.get("/languages").json()

    english = next(language for language in languages if language["code"] == "en")

    response = client.post(
        "/profile/languages",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
        },
        json={
            "language_id": english["id"],
            "type": "learning",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["language"]["code"] == "en"
    assert data["type"] == "learning"


def test_get_profile_languages(
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

    languages = client.get("/languages").json()

    english = next(language for language in languages if language["code"] == "en")

    client.post(
        "/profile/languages",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
        },
        json={
            "language_id": english["id"],
            "type": "learning",
        },
    )

    response = client.get(
        "/profile/languages",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["language"]["code"] == "en"


def test_remove_profile_language(
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

    languages = client.get("/languages").json()

    english = next(language for language in languages if language["code"] == "en")

    client.post(
        "/profile/languages",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
        },
        json={
            "language_id": english["id"],
            "type": "learning",
        },
    )

    response = client.request(
        "DELETE",
        "/profile/languages",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
        },
        json={
            "language_id": english["id"],
            "type": "learning",
        },
    )

    assert response.status_code == 200

    response = client.get(
        "/profile/languages",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
        },
    )

    assert response.json() == []


def test_cannot_add_language_without_profile(
    client,
    student_user,
):
    languages = client.get("/languages").json()

    english = next(language for language in languages if language["code"] == "en")

    response = client.post(
        "/profile/languages",
        headers={
            "Authorization": f"Bearer {student_user['access_token']}",
        },
        json={
            "language_id": english["id"],
            "type": "learning",
        },
    )

    assert response.status_code == 404
