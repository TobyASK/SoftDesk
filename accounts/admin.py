"""
Admin configuration for accounts app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Admin interface for CustomUser model.
    """
    fieldsets = UserAdmin.fieldsets + (
        ('RGPD Compliance', {
            'fields': ('age', 'can_be_contacted', 'can_data_be_shared')
        }),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'age', 'created_at')
    ordering = ('-created_at',)
