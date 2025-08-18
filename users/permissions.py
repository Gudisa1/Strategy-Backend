from rest_framework.permissions import BasePermission


class IsSysAdminOrSelf(BasePermission):
    """
    Sys Admin can manage all users.
    Non-admin can only view/update their own profile.
    """

    def has_permission(self, request, view):
        # Allow listing only for sys admins
        if view.action in ["list", "create", "destroy"]:
            return request.user.is_authenticated and request.user.is_sys_admin
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_sys_admin:
            return True
        # Non-admins can only view or edit themselves
        return obj == request.user
