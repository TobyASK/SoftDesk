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
        VÃ©rifie si l'utilisateur est contributeur du projet.

        obj peut Ãªtre :
        - Project : vÃ©rifie directement
        - Issue ou Comment : rÃ©cupÃ¨re le projet via obj.project
        """
        # obj peut Ãªtre Project, Issue, ou Comment
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
        VÃ©rifie si l'utilisateur est l'auteur du projet.
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

    RÃ¨gles :
    - GET/HEAD/OPTIONS : N'importe quel contributeur peut consulter
    - POST/PUT/PATCH/DELETE : Seul l'auteur peut modifier/supprimer
    """
    message = "Vous devez Ãªtre contributeur du projet."

    def has_object_permission(self, request, view, obj):
        """
        VÃ©rifie si l'utilisateur est contributeur (lecture) ou auteur (Ã©criture).
        """
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            # Lecture : vÃ©rifier si contributeur
            if hasattr(obj, 'project'):
                project = obj.project
            else:
                project = obj

            return Contributor.objects.filter(
                user=request.user,
                project=project
            ).exists()

        # Ã‰criture : doit Ãªtre l'auteur
        if hasattr(obj, 'author'):
            return obj.author == request.user
        return False
