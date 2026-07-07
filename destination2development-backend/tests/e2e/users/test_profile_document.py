from __future__ import annotations

from app.models.user import SystemRole


def upload_profile_document(
    client,
    access_token: str,
    document_type: str = "profile_photo",
):
    response = client.post(
        "/profile-documents",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
        json={
            "document_type": document_type,
            "file_path": "/uploads/test-avatar.png",
        },
    )

    assert response.status_code == 200

    return response.json()


def test_upload_profile_document(
    client,
    disposable_user,
):
    document = upload_profile_document(
        client,
        disposable_user["access_token"],
    )

    assert document["document_type"] == "profile_photo"
    assert document["file_path"] == "/uploads/test-avatar.png"
    assert document["verification_status"] == "pending"


def test_upload_duplicate_document_returns_conflict(
    client,
    disposable_user,
):
    upload_profile_document(
        client,
        disposable_user["access_token"],
    )

    response = client.post(
        "/profile-documents",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
        json={
            "document_type": "profile_photo",
            "file_path": "/uploads/another-avatar.png",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Document already exists."


def test_get_my_documents(
    client,
    disposable_user,
):
    upload_profile_document(
        client,
        disposable_user["access_token"],
    )

    response = client.get(
        "/profile-documents",
        headers={
            "Authorization": f"Bearer {disposable_user['access_token']}",
        },
    )

    assert response.status_code == 200

    documents = response.json()

    assert len(documents) == 1
    assert documents[0]["document_type"] == "profile_photo"


def test_admin_can_list_documents(
    client,
    disposable_user,
    admin_user,
):
    upload_profile_document(
        client,
        disposable_user["access_token"],
    )

    response = client.get(
        "/profile-documents/admin",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    assert response.status_code == 200

    documents = response.json()

    assert len(documents) >= 1


def test_admin_can_move_document_to_review(
    client,
    disposable_user,
    admin_user,
):
    document = upload_profile_document(
        client,
        disposable_user["access_token"],
    )

    response = client.patch(
        f"/profile-documents/admin/{document['id']}/review",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    assert response.status_code == 200

    updated = response.json()

    assert updated["verification_status"] == "in_review"


def test_admin_can_approve_document(
    client,
    disposable_user,
    admin_user,
):
    document = upload_profile_document(
        client,
        disposable_user["access_token"],
    )

    review_response = client.patch(
        f"/profile-documents/admin/{document['id']}/review",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    assert review_response.status_code == 200

    response = client.patch(
        f"/profile-documents/admin/{document['id']}/approve",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    assert response.status_code == 200

    updated = response.json()

    assert updated["verification_status"] == "approved"
    assert updated["verified_by"] is not None
    assert updated["verified_at"] is not None


def test_admin_cannot_approve_already_approved_document(
    client,
    disposable_user,
    admin_user,
):
    document = upload_profile_document(
        client,
        disposable_user["access_token"],
    )

    client.patch(
        f"/profile-documents/admin/{document['id']}/approve",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    response = client.patch(
        f"/profile-documents/admin/{document['id']}/approve",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid document state."


def test_admin_can_reject_document(
    client,
    disposable_user,
    admin_user,
):
    document = upload_profile_document(
        client,
        disposable_user["access_token"],
    )

    response = client.patch(
        f"/profile-documents/admin/{document['id']}/reject",
        headers={
            "Authorization": f"Bearer {admin_user['access_token']}",
        },
    )

    assert response.status_code == 200

    updated = response.json()

    assert updated["verification_status"] == "rejected"
