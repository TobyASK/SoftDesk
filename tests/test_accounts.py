"""
Tests de l'application accounts : inscription, authentification et profil.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()


@pytest.mark.django_db
class TestUserRegistration:
    """Teste l'endpoint d'inscription utilisateur."""

    def test_register_valid_user(self, api_client, user_data):
        """Vérifie une inscription utilisateur réussie."""
        response = api_client.post('/api/v1/auth/register/', user_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert 'username' in response.data
        assert response.data['username'] == user_data['username']
        assert User.objects.filter(username=user_data['username']).exists()

    def test_register_user_age_below_15(self, api_client, user_under_15_data):
        """Vérifie que l'inscription échoue pour un âge inférieur à 15 ans."""
        response = api_client.post(
            '/api/v1/auth/register/',
            user_under_15_data
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'age' in response.data
        assert not User.objects.filter(
            username=user_under_15_data['username']
        ).exists()

    def test_register_password_mismatch(self, api_client, user_data):
        """Vérifie l'échec si les mots de passe ne correspondent pas."""
        user_data['password_confirm'] = 'differentpassword'
        response = api_client.post('/api/v1/auth/register/', user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password_confirm' in response.data

    def test_register_duplicate_username(
        self,
        api_client,
        user_data,
        authenticated_user
    ):
        """Vérifie l'échec si le nom d'utilisateur existe déjà."""
        user_data['email'] = 'different@example.com'
        user_data['username'] = authenticated_user.username
        response = api_client.post('/api/v1/auth/register/', user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'username' in response.data

    def test_register_missing_required_field(self, api_client):
        """Vérifie l'échec si un champ obligatoire est absent."""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
        }
        response = api_client.post('/api/v1/auth/register/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_short_password(self, api_client, user_data):
        """Vérifie l'échec pour un mot de passe < 8 caractères."""
        user_data['password'] = 'short'
        user_data['password_confirm'] = 'short'
        response = api_client.post('/api/v1/auth/register/', user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestJWTAuthentication:
    """Teste les endpoints d'authentification JWT."""

    def test_obtain_token(self, api_client, authenticated_user):
        """Vérifie l'obtention d'un token JWT."""
        response = api_client.post('/api/v1/auth/token/', {
            'username': authenticated_user.username,
            'password': 'securepass123',
        })
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_obtain_token_invalid_credentials(
        self,
        api_client,
        authenticated_user
    ):
        """Vérifie l'échec d'obtention avec des identifiants invalides."""
        response = api_client.post('/api/v1/auth/token/', {
            'username': authenticated_user.username,
            'password': 'wrongpassword',
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_token(self, api_client, authenticated_user):
        """Vérifie le rafraîchissement du token."""
        # Récupère les tokens initiaux
        response = api_client.post('/api/v1/auth/token/', {
            'username': authenticated_user.username,
            'password': 'securepass123',
        })
        refresh_token = response.data['refresh']

        # Rafraîchit le token
        response = api_client.post('/api/v1/auth/token/refresh/', {
            'refresh': refresh_token,
        })
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

    def test_access_protected_endpoint_without_auth(self, api_client):
        """Vérifie l'échec d'accès sans authentification."""
        response = api_client.get('/api/v1/auth/users/profile/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_access_protected_endpoint_with_token(
        self,
        api_client,
        authenticated_user
    ):
        """Vérifie l'accès avec un token valide."""
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
    """Teste la consultation et la mise à jour du profil utilisateur."""

    def test_view_own_profile(self, authenticated_client, authenticated_user):
        """Vérifie la consultation de son propre profil."""
        response = authenticated_client.get('/api/v1/auth/users/profile/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == authenticated_user.username
        assert response.data['age'] == authenticated_user.age

    def test_update_own_profile(
        self,
        authenticated_client,
        authenticated_user
    ):
        """Vérifie la mise à jour de son propre profil."""
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
        """Vérifie qu'on ne peut pas modifier
        le profil d'un autre utilisateur.
        """
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
        """Vérifie la liste des utilisateurs."""
        response = authenticated_client.get('/api/v1/auth/users/')
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data  # Réponse paginée
