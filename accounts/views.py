"""
Vues pour l'application accounts - inscription et gestion du profil.
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
    ViewSet pour l'inscription, la consultation et la mise à jour du profil.

    Endpoints :
    - POST /api/v1/auth/register/ : Inscrire un nouvel utilisateur
    - GET /api/v1/auth/users/ : Lister les utilisateurs (paginé)
    - GET /api/v1/auth/users/{id}/ : Détails d'un utilisateur
    - PUT /api/v1/auth/users/{id}/ : Mettre à jour un profil utilisateur
    - GET /api/v1/auth/users/profile/me/ : Profil de l'utilisateur courant
    """
    queryset = User.objects.all()
    permission_classes = [IsOwnerOrReadOnly]

    def get_permissions(self):
        """Autorise tous les utilisateurs à s'inscrire, auth requise sinon."""
        if self.action == 'create':
            return [AllowAny()]
        elif self.action in ['profile', 'partial_update']:
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_serializer_class(self):
        """Retourne le bon sérialiseur selon l'action."""
        if self.action == 'create':
            return UserRegistrationSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserDetailSerializer

    def get_queryset(self):
        """Filtre les utilisateurs selon les permissions."""
        # Les utilisateurs ne voient que leur propre profil en détail
        if self.action == 'profile':
            return User.objects.filter(id=self.request.user.id)
        # La liste retourne tous les utilisateurs (données non sensibles)
        return User.objects.all()

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def profile(self, request):
        """Retourne le profil de l'utilisateur courant."""
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """Crée un utilisateur depuis les données d'inscription."""
        serializer.save()

    def create(self, request, *args, **kwargs):
        """Surcharge `create` pour retourner
        une réponse d'inscription propre.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )
