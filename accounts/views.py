"""
Views for accounts app - User registration and profile management.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from .serializers import (
    UserRegistrationSerializer,
    UserDetailSerializer,
    UserUpdateSerializer,
)
from .permissions import IsOwnerOrReadOnly

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User registration, profile viewing, and updates.

    Endpoints:
    - POST /api/v1/auth/register/ : Register new user
    - GET /api/v1/auth/users/ : List all users (paginated)
    - GET /api/v1/auth/users/{id}/ : Get user details
    - PUT /api/v1/auth/users/{id}/ : Update user profile
    - GET /api/v1/auth/users/profile/me/ : Get current user profile
    """
    queryset = User.objects.all()
    permission_classes = [IsOwnerOrReadOnly]

    def get_permissions(self):
        """Allow anyone to register, authenticated for other actions."""
        if self.action == 'create':
            return [AllowAny()]
        elif self.action in ['profile', 'partial_update']:
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return UserRegistrationSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserDetailSerializer

    def get_queryset(self):
        """Filter users based on permissions."""
        # Users can only see their own profile in detail
        if self.action == 'profile':
            return User.objects.filter(id=self.request.user.id)
        # List view returns all users (non-sensitive data)
        return User.objects.all()

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def profile(self, request):
        """Get current user's profile."""
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """Create user from registration data."""
        serializer.save()

    def create(self, request, *args, **kwargs):
        """Override create to return proper response on registration."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )
