from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit objects (update/delete),
    while allowing all users to view (GET) objects.
    """

    def has_permission(self, request, view):
        # Allow read-only methods for all users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Allow write permissions only for users with 'Admin' role
        return request.user and request.user.role == 'Admin'

    def has_object_permission(self, request, view, obj):
        # Allow read-only methods for all users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Allow write permissions only for users with 'Admin' role
        return request.user and request.user.role == 'Admin'
