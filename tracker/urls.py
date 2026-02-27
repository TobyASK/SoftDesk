"""
URL routing for tracker app with nested routes.
"""

from django.urls import path, include
from rest_framework.routers import SimpleRouter, DefaultRouter
from .views import ProjectViewSet, IssueViewSet, CommentViewSet

# Main router
router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')

# Nested router for issues under projects
projects_router = SimpleRouter()
projects_router.register(
    r'issues',
    IssueViewSet,
    basename='issue'
)

# Nested router for comments under issues
issues_router = SimpleRouter()
issues_router.register(
    r'comments',
    CommentViewSet,
    basename='comment'
)

urlpatterns = [
    path('', include(router.urls)),
    path('projects/<uuid:project_pk>/', include(projects_router.urls)),
    path('projects/<uuid:project_pk>/issues/<uuid:issue_pk>/', include(issues_router.urls)),
]
