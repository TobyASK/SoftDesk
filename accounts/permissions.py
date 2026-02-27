"""
Permissions for accounts app.
"""

from rest_framework.permissions import BasePermission


class IsOwnerOrReadOnly(BasePermission):
    """
    Permission to allow only the owner of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return obj.id == request.user.id
