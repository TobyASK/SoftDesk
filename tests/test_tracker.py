"""
Tests de l'application tracker : projets, issues, commentaires et permissions.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from tracker.models import Project, Contributor, Issue, Comment

User = get_user_model()


@pytest.mark.django_db
class TestProjectManagement:
    """Teste la création et la gestion des projets."""

    def test_create_project(self, authenticated_client, authenticated_user):
        """Vérifie la création d'un projet."""
        data = {
            'name': 'Test Project',
            'description': 'A test project',
            'type': 'back-end',
        }
        response = authenticated_client.post('/api/v1/projects/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == data['name']

        # Vérifie que le créateur est auteur et contributeur
        project = Project.objects.get(name=data['name'])
        assert project.author == authenticated_user
        assert Contributor.objects.filter(
            user=authenticated_user,
            project=project,
            role='author'
        ).exists()

    def test_list_user_projects(
        self,
        authenticated_client,
        authenticated_user,
        another_user
    ):
        """Vérifie la liste des projets où l'utilisateur est contributeur."""
        # Crée un projet pour l'utilisateur authentifié
        project1 = Project.objects.create(
            name='Project 1',
            description='Test',
            type='back-end',
            author=authenticated_user
        )
        Contributor.objects.create(
            user=authenticated_user,
            project=project1,
            role='author'
        )

        # Crée un projet pour un autre utilisateur (non contributeur)
        project2 = Project.objects.create(
            name='Project 2',
            description='Test',
            type='front-end',
            author=another_user
        )
        Contributor.objects.create(
            user=another_user,
            project=project2,
            role='author'
        )

        response = authenticated_client.get('/api/v1/projects/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == 'Project 1'

    def test_update_project_as_author(
        self,
        authenticated_client,
        authenticated_user
    ):
        """Vérifie la mise à jour d'un projet par son auteur."""
        project = Project.objects.create(
            name='Original Name',
            description='Original',
            type='back-end',
            author=authenticated_user
        )
        Contributor.objects.create(
            user=authenticated_user,
            project=project,
            role='author'
        )

        data = {
            'name': 'Updated Name',
            'description': 'Updated description',
            'type': 'front-end'
        }
        response = authenticated_client.put(
            f'/api/v1/projects/{project.id}/',
            data
        )
        assert response.status_code == status.HTTP_200_OK
        project.refresh_from_db()
        assert project.name == 'Updated Name'

    def test_cannot_update_project_as_non_author(
        self,
        authenticated_client,
        authenticated_user,
        another_user
    ):
        """Vérifie qu'un contributeur non-auteur ne peut pas modifier un projet.
        """
        project = Project.objects.create(
            name='Project',
            description='Test',
            type='back-end',
            author=another_user
        )
        # Ajoute l'utilisateur authentifié comme contributeur (non auteur)
        Contributor.objects.create(
            user=authenticated_user,
            project=project,
            role='contributor'
        )
        Contributor.objects.create(
            user=another_user,
            project=project,
            role='author'
        )

        data = {'name': 'Hacked Name'}
        response = authenticated_client.put(
            f'/api/v1/projects/{project.id}/',
            data
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_cannot_access_project_if_not_contributor(
        self,
        authenticated_client,
        another_user
    ):
        """Vérifie qu'un non-contributeur n'accède pas au projet."""
        project = Project.objects.create(
            name='Secret Project',
            description='Test',
            type='back-end',
            author=another_user
        )
        Contributor.objects.create(
            user=another_user,
            project=project,
            role='author'
        )

        response = authenticated_client.get(f'/api/v1/projects/{project.id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_add_contributor(
        self,
        authenticated_client,
        authenticated_user,
        another_user
    ):
        """Vérifie l'ajout d'un contributeur à un projet."""
        project = Project.objects.create(
            name='Project',
            description='Test',
            type='back-end',
            author=authenticated_user
        )
        Contributor.objects.create(
            user=authenticated_user,
            project=project,
            role='author'
        )

        data = {'user_id': another_user.id}
        response = authenticated_client.post(
            f'/api/v1/projects/{project.id}/contributor/',
            data
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert Contributor.objects.filter(
            user=another_user,
            project=project
        ).exists()

    def test_cannot_add_duplicate_contributor(
        self,
        authenticated_client,
        authenticated_user,
        another_user
    ):
        """Vérifie qu'on ne peut pas ajouter deux fois le même contributeur."""
        project = Project.objects.create(
            name='Project',
            description='Test',
            type='back-end',
            author=authenticated_user
        )
        Contributor.objects.create(
            user=authenticated_user,
            project=project,
            role='author'
        )
        Contributor.objects.create(
            user=another_user,
            project=project,
            role='contributor'
        )

        data = {'user_id': another_user.id}
        response = authenticated_client.post(
            f'/api/v1/projects/{project.id}/contributor/',
            data
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestIssueManagement:
    """Teste la création et la gestion des issues."""

    @pytest.fixture
    def project_with_contributors(self, authenticated_user, another_user):
        """Crée un projet avec deux contributeurs."""
        project = Project.objects.create(
            name='Test Project',
            description='Test',
            type='back-end',
            author=authenticated_user
        )
        Contributor.objects.create(
            user=authenticated_user,
            project=project,
            role='author'
        )
        Contributor.objects.create(
            user=another_user,
            project=project,
            role='contributor'
        )
        return project

    def test_create_issue(
        self,
        authenticated_client,
        project_with_contributors
    ):
        """Vérifie la création d'une issue."""
        data = {
            'title': 'Fix login bug',
            'description': 'Login not working',
            'priority': 'HIGH',
            'tag': 'BUG',
            'status': 'To Do',
        }
        response = authenticated_client.post(
            f'/api/v1/projects/{project_with_contributors.id}/issues/',
            data
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert Issue.objects.filter(title=data['title']).exists()

    def test_assign_issue_to_contributor(
        self,
        authenticated_client,
        authenticated_user,
        project_with_contributors
    ):
        """Vérifie l'assignation d'une issue à un contributeur du projet."""
        issue = Issue.objects.create(
            project=project_with_contributors,
            title='Test Issue',
            description='Test',
            author=authenticated_user,
        )

        # Récupère un second utilisateur contributeur du projet
        other_contributor = project_with_contributors.contributors.exclude(
            user=authenticated_user
        ).first().user

        data = {
            'assignee_id': other_contributor.id,
        }
        issue_url = (
            f'/api/v1/projects/{project_with_contributors.id}/issues/'
            f'{issue.id}/'
        )
        response = authenticated_client.patch(
            issue_url,
            data
        )
        assert response.status_code == status.HTTP_200_OK
        issue.refresh_from_db()
        assert issue.assignee == other_contributor

    def test_cannot_assign_issue_to_non_contributor(
        self,
        authenticated_client,
        authenticated_user,
        another_user,
        project_with_contributors
    ):
        """Vérifie qu'on ne peut pas assigner une issue
        à un non-contributeur.
        """
        issue = Issue.objects.create(
            project=project_with_contributors,
            title='Test Issue',
            description='Test',
            author=authenticated_user,
        )

        # Crée un utilisateur qui n'est pas contributeur
        non_contributor = User.objects.create_user(
            username='noncontributor',
            email='non@example.com',
            age=25,
            password='pass123'
        )
        data = {'assignee_id': non_contributor.id}
        issue_url = (
            f'/api/v1/projects/{project_with_contributors.id}/issues/'
            f'{issue.id}/'
        )
        response = authenticated_client.patch(
            issue_url,
            data
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'assignee_id' in response.data

    def test_update_issue_as_author(
        self,
        authenticated_client,
        authenticated_user,
        project_with_contributors
    ):
        """Vérifie la mise à jour d'une issue par son auteur."""
        issue = Issue.objects.create(
            project=project_with_contributors,
            title='Original Title',
            description='Original',
            author=authenticated_user,
        )

        data = {'status': 'In Progress', 'priority': 'HIGH'}
        issue_url = (
            f'/api/v1/projects/{project_with_contributors.id}/issues/'
            f'{issue.id}/'
        )
        response = authenticated_client.patch(
            issue_url,
            data
        )
        assert response.status_code == status.HTTP_200_OK
        issue.refresh_from_db()
        assert issue.status == 'In Progress'

    def test_cannot_update_issue_as_non_author(
        self,
        another_authenticated_client,
        authenticated_user,
        project_with_contributors
    ):
        """Vérifie qu'une issue ne peut pas être modifiée par un non-auteur."""
        issue = Issue.objects.create(
            project=project_with_contributors,
            title='Test Issue',
            description='Test',
            author=authenticated_user,
        )

        data = {'status': 'Finished'}
        issue_url = (
            f'/api/v1/projects/{project_with_contributors.id}/issues/'
            f'{issue.id}/'
        )
        response = another_authenticated_client.patch(
            issue_url,
            data
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_project_issues(
        self,
        authenticated_client,
        authenticated_user,
        project_with_contributors
    ):
        """Vérifie la liste paginée des issues d'un projet."""
        for i in range(15):
            Issue.objects.create(
                project=project_with_contributors,
                title=f'Issue {i}',
                description='Test',
                author=authenticated_user,
            )

        response = authenticated_client.get(
            f'/api/v1/projects/{project_with_contributors.id}/issues/'
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 10  # Taille de page par défaut
        assert response.data['count'] == 15


@pytest.mark.django_db
class TestCommentManagement:
    """Teste la création et la gestion des commentaires."""

    @pytest.fixture
    def issue_with_author(self, authenticated_user, project_with_contributors):
        """Crée une issue pour tester les commentaires."""
        return Issue.objects.create(
            project=project_with_contributors,
            title='Test Issue',
            description='Test',
            author=authenticated_user,
        )

    def test_create_comment(
        self,
        authenticated_client,
        project_with_contributors,
        issue_with_author
    ):
        """Vérifie la création d'un commentaire sur une issue."""
        data = {'description': 'This is a comment'}
        comments_url = (
            f'/api/v1/projects/{project_with_contributors.id}/issues/'
            f'{issue_with_author.id}/comments/'
        )
        response = authenticated_client.post(
            comments_url,
            data
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert Comment.objects.filter(
            description=data['description']
        ).exists()

    def test_update_comment_as_author(
        self,
        authenticated_client,
        authenticated_user,
        project_with_contributors,
        issue_with_author
    ):
        """Vérifie la mise à jour d'un commentaire par son auteur."""
        comment = Comment.objects.create(
            issue=issue_with_author,
            description='Original comment',
            author=authenticated_user,
        )

        data = {'description': 'Updated comment'}
        comment_url = (
            f'/api/v1/projects/{project_with_contributors.id}/issues/'
            f'{issue_with_author.id}/comments/{comment.id}/'
        )
        response = authenticated_client.patch(
            comment_url,
            data
        )
        assert response.status_code == status.HTTP_200_OK
        comment.refresh_from_db()
        assert comment.description == 'Updated comment'

    def test_cannot_update_comment_as_non_author(
        self,
        another_authenticated_client,
        authenticated_user,
        project_with_contributors,
        issue_with_author
    ):
        """Vérifie qu'un commentaire ne peut pas être modifié
        par un non-auteur.
        """
        comment = Comment.objects.create(
            issue=issue_with_author,
            description='Original comment',
            author=authenticated_user,
        )

        data = {'description': 'Hacked comment'}
        comment_url = (
            f'/api/v1/projects/{project_with_contributors.id}/issues/'
            f'{issue_with_author.id}/comments/{comment.id}/'
        )
        response = another_authenticated_client.patch(
            comment_url,
            data
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_issue_comments(
        self,
        authenticated_client,
        authenticated_user,
        project_with_contributors,
        issue_with_author
    ):
        """Vérifie la liste paginée des commentaires d'une issue."""
        for i in range(15):
            Comment.objects.create(
                issue=issue_with_author,
                description=f'Comment {i}',
                author=authenticated_user,
            )

        comments_url = (
            f'/api/v1/projects/{project_with_contributors.id}/issues/'
            f'{issue_with_author.id}/comments/'
        )
        response = authenticated_client.get(
            comments_url
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 10  # Taille de page par défaut
        assert response.data['count'] == 15


@pytest.mark.django_db
class TestUnauthenticatedAccess:
    """Vérifie que les utilisateurs non authentifiés
    n'accèdent pas aux ressources.
    """

    def test_cannot_list_projects_without_auth(self, api_client):
        """Vérifie qu'on ne peut pas lister les projets
        sans authentification.
        """
        response = api_client.get('/api/v1/projects/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cannot_create_project_without_auth(self, api_client):
        """Vérifie qu'on ne peut pas créer de projet sans authentification."""
        data = {
            'name': 'Project',
            'description': 'Test',
            'type': 'back-end',
        }
        response = api_client.post('/api/v1/projects/', data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.fixture
def project_with_contributors(authenticated_user, another_user):
    """Crée un projet avec deux contributeurs."""
    project = Project.objects.create(
        name='Test Project',
        description='Test',
        type='back-end',
        author=authenticated_user
    )
    Contributor.objects.create(
        user=authenticated_user,
        project=project,
        role='author'
    )
    Contributor.objects.create(
        user=another_user,
        project=project,
        role='contributor'
    )
    return project


@pytest.fixture
def issue_with_author(authenticated_user, project_with_contributors):
    """Crée une issue pour tester les commentaires."""
    return Issue.objects.create(
        project=project_with_contributors,
        title='Test Issue',
        description='Test',
        author=authenticated_user,
    )
