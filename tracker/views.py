"""
Vues pour l'application tracker - Gestion des projets, issues et commentaires.

Contient :
- ProjectViewSet : CRUD sur les projets + gestion des contributeurs
- IssueViewSet : CRUD sur les problÃ¨mes (issues) d'un projet
- CommentViewSet : CRUD sur les commentaires d'une issue

SÃ©curitÃ© :
- Tous les endpoints nÃ©cessitent une authentification JWT
- Les querysets sont filtrÃ©s pour ne montrer que les ressources accessibles
- Les permissions sont vÃ©rifiÃ©es Ã  chaque requÃªte
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Project, Contributor, Issue, Comment
from .serializers import (
    ProjectListSerializer,
    ProjectDetailSerializer,
    ContributorSerializer,
    IssueListSerializer,
    IssueDetailSerializer,
    CommentSerializer,
)
from .permissions import (
    IsProjectContributor,
    IsIssueOrCommentAuthor,
    IsContributorOrReadOnly,
)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des projets.

    Endpoints :
    - GET /api/v1/projects/ : Liste des projets de l'utilisateur (paginÃ©)
    - POST /api/v1/projects/ : CrÃ©er un projet (crÃ©ateur devient auteur + contributeur)
    - GET /api/v1/projects/{id}/ : DÃ©tails du projet
    - PUT /api/v1/projects/{id}/ : Modifier le projet (auteur uniquement)
    - DELETE /api/v1/projects/{id}/ : Supprimer le projet (auteur uniquement)
    - POST /api/v1/projects/{id}/contributor/ : Ajouter un contributeur
    - DELETE /api/v1/projects/{id}/contributor/?user_id=X : Retirer un contributeur

    SÃ©curitÃ© :
    - Authentification JWT requise
    - Seuls les contributeurs voient le projet
    - Seul l'auteur peut modifier/supprimer
    """
    permission_classes = [IsAuthenticated, IsContributorOrReadOnly]
    basename = 'project'

    def get_serializer_class(self):
        """Use detail serializer for retrieve/create, list serializer for list."""
        if self.action == 'list':
            return ProjectListSerializer
        return ProjectDetailSerializer

    def get_queryset(self):
        """
        Filtrage des projets : l'utilisateur doit Ãªtre contributeur.

        SÃ©curitÃ© : Seuls les projets oÃ¹ l'utilisateur est contributeur sont retournÃ©s.
        Optimisation : select_related pour l'auteur, prefetch_related pour les contributeurs.
        """
        queryset = Project.objects.filter(
            contributors__user=self.request.user
        ).distinct()

        # Optimisation des requÃªtes ORM
        if self.action == 'list':
            queryset = queryset.select_related('author').prefetch_related(
                'contributors__user'
            )
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            queryset = queryset.select_related('author').prefetch_related(
                'contributors__user'
            )

        return queryset

    def perform_create(self, serializer):
        """Créer le projet avec l'utilisateur actuel comme auteur."""
        project = serializer.save(author=self.request.user)
        # Ajouter automatiquement le créateur comme contributeur avec rôle author
        Contributor.objects.create(
            project=project,
            user=self.request.user,
            role='author'
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        basename='add-remove-contributor'
    )
    def contributor(self, request, pk=None):
        """
        Gestion des contributeurs d'un projet.

        POST /api/v1/projects/{id}/contributor/ : Ajouter un contributeur
        DELETE /api/v1/projects/{id}/contributor/?user_id=X : Retirer un contributeur

        Body (POST) :
        {
            "user_id": <user_id>
        }

        Query params (DELETE) :
        ?user_id=<user_id>

        SÃ©curitÃ© : Seuls les contributeurs du projet peuvent gÃ©rer les membres.
        """
        project = self.get_object()

        # VÃ©rifier si l'utilisateur est contributeur du projet
        if not Contributor.objects.filter(
            user=request.user,
            project=project
        ).exists():
            return Response(
                {'detail': 'Seuls les contributeurs peuvent gÃ©rer les membres du projet.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if request.method == 'POST':
            serializer = ContributorSerializer(
                data=request.data,
                context={'project': project}
            )
            if serializer.is_valid():
                serializer.save(project=project)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        elif request.method == 'DELETE':
            user_id = request.query_params.get('user_id')
            if not user_id:
                return Response(
                    {'detail': 'user_id query parameter is required.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                contributor = Contributor.objects.get(
                    user_id=user_id,
                    project=project
                )
                # Prevent removing the last contributor (project author)
                if contributor.role == 'author' and project.contributors.count() <= 1:
                    return Response(
                        {'detail': 'Cannot remove the project author when they are the only contributor.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                contributor.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Contributor.DoesNotExist:
                return Response(
                    {'detail': 'Contributor not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )


class IssueViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des problÃ¨mes (issues) dans un projet.

    Endpoints :
    - GET /api/v1/projects/{project_id}/issues/ : Liste des issues du projet (paginÃ©)
    - POST /api/v1/projects/{project_id}/issues/ : CrÃ©er une issue
    - GET /api/v1/projects/{project_id}/issues/{id}/ : DÃ©tails de l'issue
    - PUT /api/v1/projects/{project_id}/issues/{id}/ : Modifier l'issue (auteur uniquement)
    - DELETE /api/v1/projects/{project_id}/issues/{id}/ : Supprimer l'issue (auteur uniquement)

    SÃ©curitÃ© :
    - Seuls les contributeurs du projet peuvent voir les issues
    - Seul l'auteur peut modifier/supprimer son issue
    - L'assignÃ© doit Ãªtre contributeur du projet (validation dans serializer)
    """
    permission_classes = [IsAuthenticated, IsProjectContributor, IsContributorOrReadOnly]
    basename = 'issue'

    def get_serializer_class(self):
        """Use detail serializer for retrieve/create, list serializer for list."""
        if self.action == 'list':
            return IssueListSerializer
        return IssueDetailSerializer

    def get_queryset(self):
        """
        Filtrage des issues : l'utilisateur doit Ãªtre contributeur du projet.

        SÃ©curitÃ© : VÃ©rifie que l'utilisateur est contributeur avant de retourner les issues.
        Si non-contributeur, retourne un queryset vide.

        Optimisation : select_related pour auteur/assignÃ©, prefetch_related pour commentaires.
        """
        project_id = self.kwargs.get('project_pk')
        queryset = Issue.objects.filter(project_id=project_id)

        # VÃ©rifier que l'utilisateur est contributeur du projet
        if not Contributor.objects.filter(
            user=self.request.user,
            project_id=project_id
        ).exists():
            return queryset.none()

        # Optimisation des requÃªtes ORM
        if self.action == 'list':
            queryset = queryset.select_related('author', 'assignee').prefetch_related(
                'comments'
            )
        elif self.action in ['retrieve', 'update', 'partial_update']:
            queryset = queryset.select_related('author', 'assignee').prefetch_related(
                'comments__author'
            )

        return queryset

    def perform_create(self, serializer):
        """CrÃ©er l'issue avec l'utilisateur actuel comme auteur."""
        project_id = self.kwargs.get('project_pk')
        project = get_object_or_404(Project, id=project_id)
        serializer.save(
            author=self.request.user,
            project=project
        )

    def get_serializer_context(self):
        """Passer le projet au serializer pour validation (assignee doit Ãªtre contributeur)."""
        context = super().get_serializer_context()
        project_id = self.kwargs.get('project_pk')
        if project_id:
            context['project'] = get_object_or_404(Project, id=project_id)
        return context

    @action(detail=True, methods=['get'])
    def comments(self, request, project_pk=None, pk=None):
        """Get all comments for an issue (paginated)."""
        issue = self.get_object()
        queryset = issue.comments.select_related('author').order_by('-created_time')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CommentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CommentSerializer(queryset, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des commentaires sur une issue.

    Endpoints :
    - GET /api/v1/projects/{project_id}/issues/{issue_id}/comments/ : Liste des commentaires (paginé)
    - POST /api/v1/projects/{project_id}/issues/{issue_id}/comments/ : Créer un commentaire
    - GET /api/v1/projects/{project_id}/issues/{issue_id}/comments/{uuid}/ : Détails du commentaire
    - PUT /api/v1/projects/{project_id}/issues/{issue_id}/comments/{uuid}/ : Modifier (auteur uniquement)
    - DELETE /api/v1/projects/{project_id}/issues/{issue_id}/comments/{uuid}/ : Supprimer (auteur uniquement)

    Sécurité :
    - Seuls les contributeurs du projet peuvent voir les commentaires
    - Seul l'auteur peut modifier/supprimer son commentaire
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsContributorOrReadOnly]
    basename = 'comment'
    lookup_field = 'uuid'

    def get_queryset(self):
        """
        Filtrage des commentaires : l'utilisateur doit Ãªtre contributeur du projet de l'issue.

        SÃ©curitÃ© : VÃ©rifie via l'issue que l'utilisateur est contributeur du projet.
        Si non-contributeur, retourne un queryset vide.

        Optimisation : select_related pour l'auteur.
        """
        issue_id = self.kwargs.get('issue_pk')
        queryset = Comment.objects.filter(issue_id=issue_id)

        # RÃ©cupÃ©rer l'issue et vÃ©rifier que l'utilisateur est contributeur du projet
        issue = get_object_or_404(Issue, id=issue_id)
        if not Contributor.objects.filter(
            user=self.request.user,
            project=issue.project
        ).exists():
            return queryset.none()

        if self.action == 'list':
            queryset = queryset.select_related('author')

        return queryset

    def perform_create(self, serializer):
        """CrÃ©er le commentaire avec l'utilisateur actuel comme auteur."""
        issue_id = self.kwargs.get('issue_pk')
        issue = get_object_or_404(Issue, id=issue_id)
        serializer.save(
            author=self.request.user,
            issue=issue
        )

    def get_serializer_context(self):
        """Pass issue to serializer for validation."""
        context = super().get_serializer_context()
        issue_id = self.kwargs.get('issue_pk')
        if issue_id:
            context['issue'] = get_object_or_404(Issue, id=issue_id)
        return context
