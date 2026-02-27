"""
Modèle utilisateur personnalisé avec conformité RGPD.

CustomUser étend AbstractUser pour ajouter :
- Validation d'âge >= 15 ans (obligation RGPD)
- Champs de consentement (can_be_contacted, can_data_be_shared)
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from datetime import date


class CustomUser(AbstractUser):
    """
    Utilisateur personnalisé avec conformité RGPD.
    
    Champs obligatoires :
    - age : Âge de l'utilisateur (doit être >= 15 ans pour s'inscrire)
    - can_be_contacted : Consentement RGPD pour être contacté
    - can_data_be_shared : Consentement RGPD pour partage des données
    """
    # Âge de l'utilisateur - validation >= 15 ans requise (RGPD)
    age = models.IntegerField(
        null=True,
        blank=True,
        help_text="Âge de l'utilisateur. Doit être >= 15 pour s'inscrire."
    )
    # Consentement RGPD : l'utilisateur accepte d'être contacté
    can_be_contacted = models.BooleanField(
        default=False,
        help_text="RGPD : Consentement pour être contacté"
    )
    # Consentement RGPD : l'utilisateur accepte le partage de ses données
    can_data_be_shared = models.BooleanField(
        default=False,
        help_text="RGPD : Consentement pour partager les données"
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
        Validation de l'âge >= 15 ans (conformité RGPD).
        Cette méthode est appelée avant la sauvegarde pour vérifier
        que l'utilisateur a l'âge minimum légal.
        """
        super().clean()
        if self.age < 15:
            raise ValidationError(
                {'age': "L'utilisateur doit avoir au moins 15 ans pour s'inscrire."}
            )
