"""
Routage des URLs pour l'application tracker avec routes imbriquées.
"""

from django.urls import re_path, include
from rest_framework.routers import SimpleRouter, DefaultRouter
from .views import ProjectViewSet, IssueViewSet, CommentViewSet

# Routeur principal
router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')

# Routeur imbriqué pour les issues d'un projet
projects_router = SimpleRouter()
projects_router.register(
    r'issues',
    IssueViewSet,
    basename='issue'
)

# Routeur imbriqué pour les commentaires d'une issue
issues_router = SimpleRouter()
issues_router.register(
    r'comments',
    CommentViewSet,
    basename='comment'
)

# Vue personnalisée pour la création/liste des commentaires
comment_viewset = CommentViewSet.as_view({
    'post': 'create',
    'get': 'list',
})

urlpatterns = [
    # Route personnalisée (doit précéder les routes générées par les routeurs)
    re_path(r'^projects/(?P<project_pk>[0-9a-f-]+)/issues/(?P<issue_pk>[0-9a-f-]+)/comments/$',
            comment_viewset, name='comment-list-create'),

    re_path('', include(router.urls)),
    re_path(r'^projects/(?P<project_pk>[0-9a-f-]+)/', include(projects_router.urls)),
    re_path(r'^projects/(?P<project_pk>[0-9a-f-]+)/issues/(?P<issue_pk>[0-9a-f-]+)/', include(issues_router.urls)),
]
