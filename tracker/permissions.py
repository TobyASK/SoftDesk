"""
Permissions pour l'application tracker - ContrÃ´le d'accÃ¨s aux projets, issues et commentaires.

RÃ¨gles de sÃ©curitÃ© implÃ©mentÃ©es :
1. IsProjectContributor : Seuls les contributeurs peuvent accÃ©der au projet
2. IsProjectAuthor : Seul l'auteur du projet peut le modifier/supprimer
3. IsIssueOrCommentAuthor : Seul l'auteur peut modifier/supprimer issue ou comment
4. IsContributorOrReadOnly : Contributeurs en lecture, auteur en Ã©criture
"""

from rest_framework.permissions import BasePermission
from .models import Contributor


class IsProjectContributor(BasePermission):
    """
    Permission : accÃ¨s au projet uniquement si utilisateur est contributeur.

    UtilisÃ©e pour filtrer l'accÃ¨s aux projets, issues et commentaires.
    Bloque toute action (GET, POST, PUT, DELETE) si non-contributeur.
    """
    message = "Vous devez Ãªtre contributeur du projet pour y accÃ©der."

    def has_object_permission(self, request, view, obj):
        """
        Vérifie si l'utilisateur est contributeur du projet.

        obj peut être :
        - Project : vérifie directement
        - Issue : récupère le projet via obj.project
        - Comment : récupère le projet via obj.issue.project
        """
        # Déterminer le projet en fonction du type d'objet
        if hasattr(obj, 'project') and not hasattr(obj, 'issue'):
            # C'est un Project ou Issue
            project = obj.project
        elif hasattr(obj, 'issue'):
            # C'est un Comment - accéder au projet via issue
            project = obj.issue.project
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
        # Déterminer le projet en fonction du type d'objet
        if hasattr(obj, 'project') and not hasattr(obj, 'issue'):
            # C'est un Project ou Issue
            project = obj.project
        elif hasattr(obj, 'issue'):
            # C'est un Comment - accéder au projet via issue
            project = obj.issue.project
        else:
            # C'est un Project
            project = obj

        return project.author == request.user


class IsIssueOrCommentAuthor(BasePermission):
    """
    Permission : modification d'issue/comment uniquement par l'auteur.

    RÃ¨gle : Seul l'auteur d'une issue ou d'un commentaire peut le modifier/supprimer.
    Les autres contributeurs peuvent seulement consulter.
    """
    message = "Seul l'auteur peut modifier ou supprimer cette ressource."

    def has_object_permission(self, request, view, obj):
        """
        VÃ©rifie si l'utilisateur est l'auteur de l'issue ou du commentaire.
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

    def has_permission(self, request, view):
        """
        Vérifie les permissions au niveau de la vue.
        Pour les commentaires, cette méthode autorise les créations par les contributeurs.
        """
        # Autoriser POST si utilisateur est authentifié
        # (la vérification du contributeur se fera dans get_queryset du ViewSet)
        if request.method == 'POST':
            return request.user and request.user.is_authenticated
        # Pour les autres méthodes, autoriser par défaut
        return True

    def has_object_permission(self, request, view, obj):
        """
        Vérifie si l'utilisateur est contributeur (lecture) ou auteur (écriture).
        """
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            # Lecture : vérifier si contributeur
            # Déterminer le projet en fonction du type d'objet
            if hasattr(obj, 'project'):
                # C'est un Project ou Issue
                project = obj.project
            elif hasattr(obj, 'issue'):
                # C'est un Comment - accéder au projet via issue
                project = obj.issue.project
            else:
                # C'est un Project
                project = obj

            return Contributor.objects.filter(
                user=request.user,
                project=project
            ).exists()

        # Écriture : doit être l'auteur
        if hasattr(obj, 'author'):
            return obj.author == request.user
        return False
