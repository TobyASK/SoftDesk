"""
Tests for accounts app - User registration, authentication, and profile management.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()


@pytest.mark.django_db
class TestUserRegistration:
    """Test user registration endpoint."""

    def test_register_valid_user(self, api_client, user_data):
        """Test successful user registration."""
        response = api_client.post('/api/v1/auth/register/', user_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert 'username' in response.data
        assert response.data['username'] == user_data['username']
        assert User.objects.filter(username=user_data['username']).exists()

    def test_register_user_age_below_15(self, api_client, user_under_15_data):
        """Test registration fails for users under 15 years old."""
        response = api_client.post('/api/v1/auth/register/', user_under_15_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'age' in response.data
        assert not User.objects.filter(username=user_under_15_data['username']).exists()

    def test_register_password_mismatch(self, api_client, user_data):
        """Test registration fails when passwords don't match."""
        user_data['password_confirm'] = 'differentpassword'
        response = api_client.post('/api/v1/auth/register/', user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password_confirm' in response.data

    def test_register_duplicate_username(self, api_client, user_data, authenticated_user):
        """Test registration fails for duplicate username."""
        user_data['email'] = 'different@example.com'
        user_data['username'] = authenticated_user.username
        response = api_client.post('/api/v1/auth/register/', user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'username' in response.data

    def test_register_missing_required_field(self, api_client):
        """Test registration fails when required field is missing."""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
        }
        response = api_client.post('/api/v1/auth/register/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_short_password(self, api_client, user_data):
        """Test registration fails for password < 8 characters."""
        user_data['password'] = 'short'
        user_data['password_confirm'] = 'short'
        response = api_client.post('/api/v1/auth/register/', user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestJWTAuthentication:
    """Test JWT authentication endpoints."""

    def test_obtain_token(self, api_client, authenticated_user):
        """Test JWT token obtention."""
        response = api_client.post('/api/v1/auth/token/', {
            'username': authenticated_user.username,
            'password': 'securepass123',
        })
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_obtain_token_invalid_credentials(self, api_client, authenticated_user):
        """Test token obtention fails with invalid credentials."""
        response = api_client.post('/api/v1/auth/token/', {
            'username': authenticated_user.username,
            'password': 'wrongpassword',
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_token(self, api_client, authenticated_user):
        """Test token refresh."""
        # Get initial tokens
        response = api_client.post('/api/v1/auth/token/', {
            'username': authenticated_user.username,
            'password': 'securepass123',
        })
        refresh_token = response.data['refresh']

        # Refresh token
        response = api_client.post('/api/v1/auth/token/refresh/', {
            'refresh': refresh_token,
        })
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

    def test_access_protected_endpoint_without_auth(self, api_client):
        """Test accessing protected endpoint without authentication fails."""
        response = api_client.get('/api/v1/auth/users/profile/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_access_protected_endpoint_with_token(self, api_client, authenticated_user):
        """Test accessing protected endpoint with valid token."""
        response = api_client.post('/api/v1/auth/token/', {
            'username': authenticated_user.username,
            'password': 'securepass123',
        })
        token = response.data['access']

        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = api_client.get('/api/v1/auth/users/profile/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == authenticated_user.username


@pytest.mark.django_db
class TestUserProfile:
    """Test user profile viewing and updating."""

    def test_view_own_profile(self, authenticated_client, authenticated_user):
        """Test viewing own profile."""
        response = authenticated_client.get('/api/v1/auth/users/profile/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == authenticated_user.username
        assert response.data['age'] == authenticated_user.age

    def test_update_own_profile(self, authenticated_client, authenticated_user):
        """Test updating own profile."""
        data = {
            'email': 'newemail@example.com',
            'first_name': 'NewFirst',
            'can_be_contacted': True,
        }
        response = authenticated_client.put(
            f'/api/v1/auth/users/{authenticated_user.id}/',
            data
        )
        assert response.status_code == status.HTTP_200_OK
        authenticated_user.refresh_from_db()
        assert authenticated_user.email == 'newemail@example.com'
        assert authenticated_user.first_name == 'NewFirst'

    def test_cannot_update_other_user_profile(
        self,
        authenticated_client,
        authenticated_user,
        another_user
    ):
        """Test cannot update other user's profile."""
        data = {
            'email': 'hacked@example.com',
            'first_name': 'Hacked',
        }
        response = authenticated_client.put(
            f'/api/v1/auth/users/{another_user.id}/',
            data
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        another_user.refresh_from_db()
        assert another_user.email != 'hacked@example.com'

    def test_list_users(self, authenticated_client):
        """Test listing users."""
        response = authenticated_client.get('/api/v1/auth/users/')
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data  # Paginated response
