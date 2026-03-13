"""
Configuration de l'admin pour l'application tracker.
"""

from django.contrib import admin
from .models import Project, Contributor, Issue, Comment


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Interface d'administration pour le modèle `Project`."""
    list_display = ('name', 'type', 'author', 'created_time')
    list_filter = ('type', 'created_time')
    search_fields = ('name', 'description', 'author__username')
    readonly_fields = ('id', 'created_time', 'updated_time')
    fieldsets = (
        ('Project Info', {
            'fields': ('id', 'name', 'description', 'type')
        }),
        ('Metadata', {
            'fields': ('author', 'created_time', 'updated_time')
        }),
    )


@admin.register(Contributor)
class ContributorAdmin(admin.ModelAdmin):
    """Interface d'administration pour le modèle `Contributor`."""
    list_display = ('user', 'project', 'role', 'created_time')
    list_filter = ('role', 'created_time')
    search_fields = ('user__username', 'project__name')
    readonly_fields = ('id', 'created_time')
    fieldsets = (
        ('Contributor Info', {
            'fields': ('id', 'user', 'project', 'role')
        }),
        ('Metadata', {
            'fields': ('created_time',)
        }),
    )


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    """Interface d'administration pour le modèle `Issue`."""
    list_display = (
        'title', 'project', 'priority', 'tag', 'status', 'author',
        'created_time'
    )
    list_filter = ('priority', 'tag', 'status', 'created_time')
    search_fields = (
        'title', 'description', 'project__name', 'author__username'
    )
    readonly_fields = ('id', 'created_time', 'updated_time')
    fieldsets = (
        ('Issue Info', {
            'fields': ('id', 'project', 'title', 'description')
        }),
        ('Status & Properties', {
            'fields': ('priority', 'tag', 'status')
        }),
        ('Assignment', {
            'fields': ('author', 'assignee')
        }),
        ('Metadata', {
            'fields': ('created_time', 'updated_time')
        }),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Interface d'administration pour le modèle `Comment`."""
    list_display = ('id', 'issue', 'author', 'created_time')
    list_filter = ('created_time',)
    search_fields = ('description', 'issue__title', 'author__username')
    readonly_fields = ('id', 'created_time', 'updated_time')
    fieldsets = (
        ('Comment Info', {
            'fields': ('id', 'issue', 'description')
        }),
        ('Metadata', {
            'fields': ('author', 'created_time', 'updated_time')
        }),
    )
