"""
ModÃ¨les pour l'application tracker - Gestion de projets et suivi des problÃ¨mes.

Relations :
- Project : Ressource principale crÃ©Ã©e par un auteur
- Contributor : Lien M2M entre User et Project (dÃ©finit l'accÃ¨s)
- Issue : ProblÃ¨me/tÃ¢che dans un projet (assignable Ã  un contributeur)
- Comment : Commentaire sur un problÃ¨me

RÃ¨gles de sÃ©curitÃ© :
- Seuls les contributeurs peuvent accÃ©der Ã  un projet
- Seul l'auteur peut modifier/supprimer ses ressources
- L'assignÃ© d'un problÃ¨me doit Ãªtre contributeur du projet
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import uuid

User = get_user_model()


class Project(models.Model):
    """
    Projet - Ressource principale de l'application.

    Le crÃ©ateur devient automatiquement auteur + contributeur.
    Seuls les contributeurs peuvent voir le projet.
    Seul l'auteur peut le modifier/supprimer.
    """
    TYPE_CHOICES = [
        ('back-end', 'Back-end'),
        ('front-end', 'Front-end'),
        ('iOS', 'iOS'),
        ('Android', 'Android'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    # Auteur du projet (crÃ©ateur)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='authored_projects'
    )
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ['-created_time']

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

    def save(self, *args, **kwargs):
        """
        CrÃ©ation automatique du contributeur pour l'auteur.
        Lors de la crÃ©ation d'un projet, l'auteur devient automatiquement
        contributeur avec le rÃ´le 'author'.
        """
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            Contributor.objects.get_or_create(
                user=self.author,
                project=self,
                defaults={'role': 'author'}
            )


class Contributor(models.Model):
    """
    Contributeur - Lien entre un utilisateur et un projet.

    DÃ©finit les droits d'accÃ¨s Ã  un projet :
    - 'author' : CrÃ©ateur du projet (peut tout modifier)
    - 'contributor' : Contributeur simple (peut voir et crÃ©er issues/comments)

    RÃ¨gle : Seuls les contributeurs peuvent accÃ©der au projet.
    """
    ROLE_CHOICES = [
        ('author', 'Author'),
        ('contributor', 'Contributor'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='contributor_projects'
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='contributors'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='contributor'
    )
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Contributor"
        verbose_name_plural = "Contributors"
        unique_together = ('user', 'project')
        ordering = ['-created_time']

    def __str__(self):
        return f"{self.user.username} - {self.project.name} ({self.get_role_display()})"


class Issue(models.Model):
    """
    ProblÃ¨me/TÃ¢che dans un projet.

    CaractÃ©ristiques :
    - PrioritÃ© : LOW, MEDIUM, HIGH
    - Tag : BUG, FEATURE, TASK
    - Statut : To Do, In Progress, Finished
    - Assignee : Utilisateur assignÃ© (doit Ãªtre contributeur du projet)

    RÃ¨gles :
    - Seuls les contributeurs du projet peuvent voir les issues
    - Seul l'auteur peut modifier/supprimer l'issue
    - L'assignÃ© doit Ãªtre contributeur (validation dans clean())
    """
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ]

    TAG_CHOICES = [
        ('BUG', 'Bug'),
        ('FEATURE', 'Feature'),
        ('TASK', 'Task'),
    ]

    STATUS_CHOICES = [
        ('To Do', 'To Do'),
        ('In Progress', 'In Progress'),
        ('Finished', 'Finished'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='issues'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='MEDIUM'
    )
    tag = models.CharField(
        max_length=20,
        choices=TAG_CHOICES,
        default='TASK'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='To Do'
    )
    # Utilisateur assignÃ© au problÃ¨me (doit Ãªtre contributeur du projet)
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_issues',
        help_text="Doit Ãªtre un contributeur du projet"
    )
    # Auteur du problÃ¨me
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_issues'
    )
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Issue"
        verbose_name_plural = "Issues"
        ordering = ['-created_time']

    def __str__(self):
        return f"{self.title} [{self.get_tag_display()}]"

    def clean(self):
        """
        Validation : l'assignÃ© doit Ãªtre contributeur du projet.
        Cette rÃ¨gle garantit que seuls les contributeurs peuvent Ãªtre assignÃ©s.
        """
        super().clean()
        if self.assignee:
            if not Contributor.objects.filter(
                user=self.assignee,
                project=self.project
            ).exists():
                raise ValidationError({
                    'assignee': "L'assignÃ© doit Ãªtre un contributeur du projet."
                })


class Comment(models.Model):
    """
    Commentaire sur un problÃ¨me (Issue).

    Utilise un UUID comme identifiant primaire.
    Seuls les contributeurs du projet peuvent voir/crÃ©er des commentaires.
    Seul l'auteur peut modifier/supprimer son commentaire.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    description = models.TextField()
    # Auteur du commentaire
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_comments'
    )
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ['-created_time']

    def __str__(self):
        return f"Comment on {self.issue.title} by {self.author.username}"
