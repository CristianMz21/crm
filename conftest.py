"""Project-wide pytest configuration and shared fixtures."""

import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    """DRF APIClient without authentication. Tests that need auth
    call `api_client.force_authenticate(user=...)` explicitly."""
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, django_user_model):
    """DRF APIClient authenticated as a fresh owner user."""
    user = django_user_model.objects.create_user(
        username="owner",
        email="owner@test.local",
        password="testpass123",
    )
    api_client.force_authenticate(user=user)
    return api_client, user
