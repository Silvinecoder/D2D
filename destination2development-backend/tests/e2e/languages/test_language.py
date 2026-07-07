def test_list_languages(
    client,
):
    response = client.get(
        "/languages",
    )

    assert response.status_code == 200

    languages = response.json()

    assert len(languages) > 0

    codes = [
        language["code"]
        for language in languages
    ]

    assert "en" in codes
    assert "pt" in codes