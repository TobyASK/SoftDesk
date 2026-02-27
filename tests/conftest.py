"""
Fixtures and configuration for tests.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.fixture
def api_client():
    """Provide APIClient instance."""
    return APIClient()


@pytest.fixture
def user_data():
    """Provide valid user registration data."""
    return {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'age': 25,
        'password': 'securepass123',
        'password_confirm': 'securepass123',
        'can_be_contacted': True,
        'can_data_be_shared': False,
    }


@pytest.fixture
def user_under_15_data():
    """Provide user data with age < 15 (should fail)."""
    return {
        'username': 'younguser',
        'email': 'young@example.com',
        'first_name': 'Young',
        'last_name': 'User',
        'age': 14,
        'password': 'securepass123',
        'password_confirm': 'securepass123',
        'can_be_contacted': True,
        'can_data_be_shared': False,
    }


@pytest.fixture
def authenticated_user(user_data):
    """Create and return authenticated user."""
    user = User.objects.create_user(
        username=user_data['username'],
        email=user_data['email'],
        first_name=user_data['first_name'],
        last_name=user_data['last_name'],
        age=user_data['age'],
        password=user_data['password'],
    )
    return user


@pytest.fixture
def authenticated_client(api_client, authenticated_user):
    """Provide APIClient with authentication."""
    refresh = RefreshToken.for_user(authenticated_user)
    api_client.credentials(
        HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}'
    )
    return api_client


@pytest.fixture
def another_user():
    """Create another authenticated user."""
    return User.objects.create_user(
        username='anotheruser',
        email='another@example.com',
        first_name='Another',
        last_name='User',
        age=30,
        password='securepass123',
    )


@pytest.fixture
def another_authenticated_client(api_client, another_user):
    """Provide APIClient with authentication for another user."""
    refresh = RefreshToken.for_user(another_user)
    api_client.credentials(
        HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}'
    )
    return api_client
