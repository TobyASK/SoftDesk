"""
SÃ©rialiseurs pour l'application accounts (gestion des utilisateurs).

Contient :
- UserRegistrationSerializer : Inscription avec validation d'Ã¢ge >= 15
- UserDetailSerializer : Affichage du profil utilisateur
- UserUpdateSerializer : Modification du profil
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    SÃ©rialiseur pour l'inscription d'un utilisateur.

    Validations :
    - Ã‚ge >= 15 ans (RGPD)
    - Mot de passe >= 8 caractÃ¨res
    - Confirmation du mot de passe
    - Nom d'utilisateur unique
    """
    # Mot de passe (non visible dans les rÃ©ponses API)
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    # Confirmation du mot de passe
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    # Ã‚ge avec validation minimum 15 ans
    age = serializers.IntegerField(min_value=15, max_value=150)
    # Consentements RGPD
    can_be_contacted = serializers.BooleanField(default=False)
    can_data_be_shared = serializers.BooleanField(default=False)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'age',
            'password',
            'password_confirm',
            'can_be_contacted',
            'can_data_be_shared',
        ]

    def validate_password(self, value):
        """Validate password strength."""
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long."
            )
        return value

    def validate_age(self, value):
        """
        Validation de l'Ã¢ge minimum (15 ans) - ConformitÃ© RGPD.
        Cette validation est critique pour l'inscription.
        """
        if value < 15:
            raise serializers.ValidationError(
                "L'utilisateur doit avoir au moins 15 ans pour s'inscrire."
            )
        return value

    def validate(self, attrs):
        """
        Validation globale : vÃ©rification que les mots de passe correspondent
        et que le nom d'utilisateur n'est pas dÃ©jÃ  pris.
        """
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({
                'password_confirm': 'Les mots de passe ne correspondent pas.'
            })

        if User.objects.filter(username=attrs.get('username')).exists():
            raise serializers.ValidationError({
                'username': 'Ce nom d\'utilisateur est dÃ©jÃ  utilisÃ©.'
            })

        return attrs

    def create(self, validated_data):
        """
        CrÃ©ation de l'utilisateur avec hachage du mot de passe.
        Le mot de passe est hachÃ© avec set_password() pour la sÃ©curitÃ©.
        """
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # Hash le mot de passe
        user.full_clean()  # Validation finale (age >= 15)
        user.save()
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile details.
    """
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'age',
            'can_be_contacted',
            'can_data_be_shared',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile updates.
    """
    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'can_be_contacted',
            'can_data_be_shared',
        ]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom token serializer to include user details.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        return token
