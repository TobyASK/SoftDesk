"""
Permissions pour l'application tracker - Contrôle d'accès aux projets, issues et commentaires.

Règles de sécurité implémentées :
1. IsProjectContributor : Seuls les contributeurs peuvent accéder au projet
2. IsProjectAuthor : Seul l'auteur du projet peut le modifier/supprimer
3. IsIssueOrCommentAuthor : Seul l'auteur peut modifier/supprimer issue ou comment
4. IsContributorOrReadOnly : Contributeurs en lecture, auteur en écriture
"""

from rest_framework.permissions import BasePermission
from .models import Contributor


class IsProjectContributor(BasePermission):
    """
    Permission : accès au projet uniquement si utilisateur est contributeur.
    
    Utilisée pour filtrer l'accès aux projets, issues et commentaires.
    Bloque toute action (GET, POST, PUT, DELETE) si non-contributeur.
    """
    message = "Vous devez être contributeur du projet pour y accéder."

    def has_object_permission(self, request, view, obj):
        """
        Vérifie si l'utilisateur est contributeur du projet.
        
        obj peut être :
        - Project : vérifie directement
        - Issue ou Comment : récupère le projet via obj.project
        """
        # obj peut être Project, Issue, ou Comment
        if hasattr(obj, 'project'):
            # C'est un Issue ou Comment
            project = obj.project
        else:
            # C'est un Project
            project = obj

        return Contributor.objects.filter(
            user=request.user,
            project=project
        ).exists()


class IsProjectAuthor(BasePermission):
    """
    Permission : gestion du projet uniquement si utilisateur est l'auteur.
    
    L'auteur du projet a tous les droits (modification, suppression, ajout de contributeurs).
    Les autres contributeurs peuvent seulement consulter.
    """
    message = "Seul l'auteur du projet peut effectuer cette action."

    def has_object_permission(self, request, view, obj):
        """
        Vérifie si l'utilisateur est l'auteur du projet.
        """
        if hasattr(obj, 'project'):
            # C'est un Issue ou Comment
            project = obj.project
        else:
            # C'est un Project
            project = obj

        return project.author == request.user


class IsIssueOrCommentAuthor(BasePermission):
    """
    Permission : modification d'issue/comment uniquement par l'auteur.
    
    Règle : Seul l'auteur d'une issue ou d'un commentaire peut le modifier/supprimer.
    Les autres contributeurs peuvent seulement consulter.
    """
    message = "Seul l'auteur peut modifier ou supprimer cette ressource."

    def has_object_permission(self, request, view, obj):
        """
        Vérifie si l'utilisateur est l'auteur de l'issue ou du commentaire.
        """
        return obj.author == request.user


class IsContributorOrReadOnly(BasePermission):
    """
    Permission : consultation si contributeur, modification si auteur.
    
    Règles :
    - GET/HEAD/OPTIONS : N'importe quel contributeur peut consulter
    - POST/PUT/PATCH/DELETE : Seul l'auteur peut modifier/supprimer
    """
    message = "Vous devez être contributeur du projet."

    def has_object_permission(self, request, view, obj):
        """
        Vérifie si l'utilisateur est contributeur (lecture) ou auteur (écriture).
        """
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            # Lecture : vérifier si contributeur
            if hasattr(obj, 'project'):
                project = obj.project
            else:
                project = obj

            return Contributor.objects.filter(
                user=request.user,
                project=project
            ).exists()

        # Écriture : doit être l'auteur
        if hasattr(obj, 'author'):
            return obj.author == request.user
        return False
