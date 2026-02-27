"""
URL routing for accounts app.
"""

from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import UserViewSet

router = SimpleRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'register', UserViewSet, basename='register')

urlpatterns = [
    path('', include(router.urls)),
]
