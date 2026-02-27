"""
Admin configuration for tracker app.
"""

from django.contrib import admin
from .models import Project, Contributor, Issue, Comment


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin interface for Project model."""
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
    """Admin interface for Contributor model."""
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
    """Admin interface for Issue model."""
    list_display = ('title', 'project', 'priority', 'tag', 'status', 'author', 'created_time')
    list_filter = ('priority', 'tag', 'status', 'created_time')
    search_fields = ('title', 'description', 'project__name', 'author__username')
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
    """Admin interface for Comment model."""
    list_display = ('uuid', 'issue', 'author', 'created_time')
    list_filter = ('created_time',)
    search_fields = ('description', 'issue__title', 'author__username')
    readonly_fields = ('uuid', 'created_time', 'updated_time')
    fieldsets = (
        ('Comment Info', {
            'fields': ('uuid', 'issue', 'description')
        }),
        ('Metadata', {
            'fields': ('author', 'created_time', 'updated_time')
        }),
    )
