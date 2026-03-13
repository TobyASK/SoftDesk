"""
Sérialiseurs pour l'application tracker.

Contient :
- ProjectListSerializer / ProjectDetailSerializer : Gestion des projets
- ContributorSerializer : Gestion des contributeurs
- IssueListSerializer / IssueDetailSerializer : Gestion des problèmes (issues)
- CommentSerializer : Gestion des commentaires

Validations métier importantes :
- L'assigné d'une issue doit être contributeur du projet
- Pas de doublons de contributeurs
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Project, Contributor, Issue, Comment

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """Informations de base sur un utilisateur en sérialisation imbriquée."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class ContributorSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour Contributor.

    Validation : Empêche les doublons.

    Un utilisateur ne peut être contributeur qu'une fois.
    """
    user = UserBasicSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='user'
    )

    class Meta:
        model = Contributor
        fields = ['id', 'user', 'user_id', 'project', 'role', 'created_time']
        read_only_fields = ['id', 'created_time', 'project']

    def validate_user_id(self, value):
        """Vérifie que l'utilisateur existe."""
        if not User.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Utilisateur introuvable.")
        return value

    def create(self, validated_data):
        """
        Empêcher les doublons.

        Un utilisateur ne peut être contributeur qu'une fois.
        """
        contributor, created = Contributor.objects.get_or_create(
            **validated_data
        )
        if not created:
            raise serializers.ValidationError(
                "Cet utilisateur est déjà contributeur de ce projet."
            )
        return contributor


class ProjectListSerializer(serializers.ModelSerializer):
    """Sérialiseur pour la liste des projets (vue simplifiée)."""
    author = UserBasicSerializer(read_only=True)
    contributors_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'type',
            'author',
            'contributors_count',
            'created_time'
        ]
        read_only_fields = ['id', 'author', 'created_time']

    def get_contributors_count(self, obj):
        """Nombre de contributeurs du projet."""
        return obj.contributors.count()


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les détails d'un projet (vue complète)."""
    author = UserBasicSerializer(read_only=True)
    contributors = ContributorSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'description',
            'type',
            'author',
            'contributors',
            'created_time',
            'updated_time'
        ]
        read_only_fields = ['id', 'author', 'created_time', 'updated_time']


class CommentSerializer(serializers.ModelSerializer):
    """Sérialiseur pour le modèle `Comment`."""
    author = UserBasicSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id',
            'description',
            'author',
            'issue',
            'created_time',
            'updated_time'
        ]
        read_only_fields = [
            'id',
            'author',
            'issue',
            'created_time',
            'updated_time',
        ]

    def validate_issue(self, value):
        """Vérifie que l'issue existe."""
        if not Issue.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Issue introuvable.")
        return value


class IssueListSerializer(serializers.ModelSerializer):
    """Sérialiseur pour la vue liste des issues."""
    author = UserBasicSerializer(read_only=True)
    assignee = UserBasicSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Issue
        fields = [
            'id',
            'title',
            'priority',
            'tag',
            'status',
            'author',
            'assignee',
            'comments_count',
            'created_time'
        ]
        read_only_fields = ['id', 'author', 'created_time']

    def get_comments_count(self, obj):
        """Retourne le nombre de commentaires d'une issue."""
        return obj.comments.count()


class IssueDetailSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour les détails d'une issue (avec commentaires).

    Validation critique : L'assigné doit être contributeur du projet.
    """
    author = UserBasicSerializer(read_only=True, allow_null=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
        source='assignee'
    )
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Issue
        fields = [
            'id',
            'project',
            'title',
            'description',
            'priority',
            'tag',
            'status',
            'author',
            'assignee_id',
            'comments',
            'created_time',
            'updated_time'
        ]
        read_only_fields = [
            'id',
            'author',
            'project',
            'created_time',
            'updated_time',
        ]

    def validate_assignee_id(self, value):
        """
        Validation critique : L'assigné doit être contributeur du projet.

        Cette validation empêche d'assigner une issue à quelqu'un
        qui n'a pas accès au projet.
        Le projet est récupéré depuis le contexte (passé par la vue).
        """
        if value is None:
            return value

        project = self.context.get('project')
        if not project:
            # Fallback : récupérer depuis l'instance si modification
            if self.instance:
                project = self.instance.project
            else:
                raise serializers.ValidationError(
                    "Les informations du projet sont nécessaires "
                    "pour valider l'assigné."
                )

        if not Contributor.objects.filter(
            user=value,
            project=project
        ).exists():
            raise serializers.ValidationError(
                "L'assigné doit être un contributeur du projet."
            )
        return value

    def create(self, validated_data):
        """Définir l'auteur comme utilisateur actuel lors de la création."""
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, attrs):
        """Validation des données saisies."""
        return attrs
