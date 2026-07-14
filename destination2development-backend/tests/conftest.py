from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.user import SystemRole

from tests.e2e.helpers.e2e_user_factory import create_e2e_user


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def disposable_user(client):
    user = create_e2e_user(
        client,
        role=SystemRole.user,
    )

    try:
        yield user
    finally:
        user["cleanup"]()


@pytest.fixture
def admin_user(client):
    user = create_e2e_user(
        client,
        role=SystemRole.admin,
    )

    try:
        yield user
    finally:
        user["cleanup"]()

@pytest.fixture
def admin_user_two(client):
    user = create_e2e_user(
        client,
        role=SystemRole.admin,
    )

    try:
        yield user
    finally:
        user["cleanup"]()
