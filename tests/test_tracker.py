"""
Tests for tracker app - Project, Issue, Comment management and permissions.
"""

import pytest
from rest_framework import status
from tracker.models import Project, Contributor, Issue, Comment


@pytest.mark.django_db
class TestProjectManagement:
    """Test project creation and management."""

    def test_create_project(self, authenticated_client, authenticated_user):
        """Test creating a project."""
        data = {
            'name': 'Test Project',
            'description': 'A test project',
            'type': 'back-end',
        }
        response = authenticated_client.post('/api/v1/projects/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == data['name']

        # Verify creator is author and contributor
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
        """Test listing only user's projects (where they are contributor)."""
        # Create project by authenticated user
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

        # Create project by another user (authenticated_user is not contributor)
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

    def test_update_project_as_author(self, authenticated_client, authenticated_user):
        """Test project update by author."""
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

        data = {'name': 'Updated Name', 'type': 'front-end'}
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
        """Test project cannot be updated by non-author contributor."""
        project = Project.objects.create(
            name='Project',
            description='Test',
            type='back-end',
            author=another_user
        )
        # Add authenticated_user as contributor (not author)
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
        """Test cannot access project if not a contributor."""
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

    def test_add_contributor(self, authenticated_client, authenticated_user, another_user):
        """Test adding a contributor to a project."""
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
        """Test cannot add same contributor twice."""
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
    """Test issue creation and management."""

    @pytest.fixture
    def project_with_contributors(self, authenticated_user, another_user):
        """Create project with two contributors."""
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

    def test_create_issue(self, authenticated_client, project_with_contributors):
        """Test creating an issue."""
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
        """Test assigning issue to a project contributor."""
        issue = Issue.objects.create(
            project=project_with_contributors,
            title='Test Issue',
            description='Test',
            author=authenticated_user,
        )

        # Create a second user who is a contributor
        other_contributor = project_with_contributors.contributors.exclude(
            user=authenticated_user
        ).first().user

        data = {
            'assignee_id': other_contributor.id,
        }
        response = authenticated_client.patch(
            f'/api/v1/projects/{project_with_contributors.id}/issues/{issue.id}/',
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
        """Test cannot assign issue to non-contributor."""
        issue = Issue.objects.create(
            project=project_with_contributors,
            title='Test Issue',
            description='Test',
            author=authenticated_user,
        )

        # Create user who is not contributor
        non_contributor = User.objects.create_user(
            username='noncontributor',
            email='non@example.com',
            age=25,
            password='pass123'
        )

        data = {'assignee_id': non_contributor.id}
        response = authenticated_client.patch(
            f'/api/v1/projects/{project_with_contributors.id}/issues/{issue.id}/',
            data
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'assignee' in response.data

    def test_update_issue_as_author(
        self,
        authenticated_client,
        authenticated_user,
        project_with_contributors
    ):
        """Test issue update by author."""
        issue = Issue.objects.create(
            project=project_with_contributors,
            title='Original Title',
            description='Original',
            author=authenticated_user,
        )

        data = {'status': 'In Progress', 'priority': 'HIGH'}
        response = authenticated_client.patch(
            f'/api/v1/projects/{project_with_contributors.id}/issues/{issue.id}/',
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
        """Test issue cannot be updated by non-author."""
        issue = Issue.objects.create(
            project=project_with_contributors,
            title='Test Issue',
            description='Test',
            author=authenticated_user,
        )

        data = {'status': 'Finished'}
        response = another_authenticated_client.patch(
            f'/api/v1/projects/{project_with_contributors.id}/issues/{issue.id}/',
            data
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_project_issues(
        self,
        authenticated_client,
        authenticated_user,
        project_with_contributors
    ):
        """Test listing issues of a project (paginated)."""
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
        assert len(response.data['results']) == 10  # Default page size
        assert response.data['count'] == 15


@pytest.mark.django_db
class TestCommentManagement:
    """Test comment creation and management."""

    @pytest.fixture
    def issue_with_author(self, authenticated_user, project_with_contributors):
        """Create issue for testing comments."""
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
        """Test creating a comment on an issue."""
        data = {'description': 'This is a comment'}
        response = authenticated_client.post(
            f'/api/v1/projects/{project_with_contributors.id}/issues/{issue_with_author.id}/comments/',
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
        """Test comment update by author."""
        comment = Comment.objects.create(
            issue=issue_with_author,
            description='Original comment',
            author=authenticated_user,
        )

        data = {'description': 'Updated comment'}
        response = authenticated_client.patch(
            f'/api/v1/projects/{project_with_contributors.id}/issues/{issue_with_author.id}/comments/{comment.uuid}/',
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
        """Test comment cannot be updated by non-author."""
        comment = Comment.objects.create(
            issue=issue_with_author,
            description='Original comment',
            author=authenticated_user,
        )

        data = {'description': 'Hacked comment'}
        response = another_authenticated_client.patch(
            f'/api/v1/projects/{project_with_contributors.id}/issues/{issue_with_author.id}/comments/{comment.uuid}/',
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
        """Test listing comments of an issue (paginated)."""
        for i in range(15):
            Comment.objects.create(
                issue=issue_with_author,
                description=f'Comment {i}',
                author=authenticated_user,
            )

        response = authenticated_client.get(
            f'/api/v1/projects/{project_with_contributors.id}/issues/{issue_with_author.id}/comments/'
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 10  # Default page size
        assert response.data['count'] == 15


@pytest.mark.django_db
class TestUnauthenticatedAccess:
    """Test that unauthenticated users cannot access resources."""

    def test_cannot_list_projects_without_auth(self, api_client):
        """Test cannot list projects without authentication."""
        response = api_client.get('/api/v1/projects/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cannot_create_project_without_auth(self, api_client):
        """Test cannot create project without authentication."""
        data = {
            'name': 'Project',
            'description': 'Test',
            'type': 'back-end',
        }
        response = api_client.post('/api/v1/projects/', data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Import needed for test_cannot_assign_issue_to_non_contributor
from django.contrib.auth import get_user_model
User = get_user_model()


@pytest.fixture
def project_with_contributors(authenticated_user, another_user):
    """Create project with two contributors."""
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
    """Create issue for testing comments."""
    return Issue.objects.create(
        project=project_with_contributors,
        title='Test Issue',
        description='Test',
        author=authenticated_user,
    )
