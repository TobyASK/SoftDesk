"""
URL routing for tracker app with nested routes.
"""

from django.urls import re_path, include
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

# Custom view for comment creation
comment_viewset = CommentViewSet.as_view({
    'post': 'create',
    'get': 'list',
})

urlpatterns = [
    # Custom route for comment creation (must come before the router routes)
    re_path(r'^projects/(?P<project_pk>[0-9a-f-]+)/issues/(?P<issue_pk>[0-9a-f-]+)/comments/$',
            comment_viewset, name='comment-list-create'),
    
    re_path('', include(router.urls)),
    re_path(r'^projects/(?P<project_pk>[0-9a-f-]+)/', include(projects_router.urls)),
    re_path(r'^projects/(?P<project_pk>[0-9a-f-]+)/issues/(?P<issue_pk>[0-9a-f-]+)/', include(issues_router.urls)),
]
