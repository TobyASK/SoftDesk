"""
ModÃ¨le utilisateur personnalisÃ© avec conformitÃ© RGPD.

CustomUser Ã©tend AbstractUser pour ajouter :
- Validation d'Ã¢ge >= 15 ans (obligation RGPD)
- Champs de consentement (can_be_contacted, can_data_be_shared)
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


class CustomUser(AbstractUser):
    """
    Utilisateur personnalisÃ© avec conformitÃ© RGPD.

    Champs obligatoires :
    - age : Ã‚ge de l'utilisateur (doit Ãªtre >= 15 ans pour s'inscrire)
    - can_be_contacted : Consentement RGPD pour Ãªtre contactÃ©
    - can_data_be_shared : Consentement RGPD pour partage des donnÃ©es
    """
    # Ã‚ge de l'utilisateur - validation >= 15 ans requise (RGPD)
    age = models.IntegerField(
        null=True,
        blank=True,
        help_text="Ã‚ge de l'utilisateur. Doit Ãªtre >= 15 pour s'inscrire."
    )
    # Consentement RGPD : l'utilisateur accepte d'Ãªtre contactÃ©
    can_be_contacted = models.BooleanField(
        default=False,
        help_text="RGPD : Consentement pour Ãªtre contactÃ©"
    )
    # Consentement RGPD : l'utilisateur accepte le partage de ses donnÃ©es
    can_data_be_shared = models.BooleanField(
        default=False,
        help_text="RGPD : Consentement pour partager les donnÃ©es"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} ({self.get_full_name()})"

    def clean(self):
        """
        Validation de l'Ã¢ge >= 15 ans (conformitÃ© RGPD).
        Cette mÃ©thode est appelÃ©e avant la sauvegarde pour vÃ©rifier
        que l'utilisateur a l'Ã¢ge minimum lÃ©gal.
        """
        super().clean()
        if self.age < 15:
            raise ValidationError(
                {'age': "L'utilisateur doit avoir au moins 15 ans pour s'inscrire."}
            )
