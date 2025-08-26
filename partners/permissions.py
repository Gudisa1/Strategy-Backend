from rest_framework import permissions

from rest_framework import permissions


class IsSysAdminOrDepartmentUser(permissions.BasePermission):
    """
    Permissions for Partner:
    - SysAdmin can do everything
    - Authenticated department users can create partners
    - Object-level: department users can update/delete only if partner is linked to their department
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if getattr(request.user, "is_sys_admin", False):
            return True
        # Allow any authenticated department user to create
        if view.action == "create":
            return request.user.departments.exists()
        # Allow listing for any authenticated user (optional)
        if view.action in ["list"]:
            return True
        # Other actions will check object-level
        return True

    def has_object_permission(self, request, view, obj):
        if getattr(request.user, "is_sys_admin", False):
            return True
        # Only department users whose departments are linked to the partner
        return bool(request.user.departments.all().intersection(obj.departments.all()))
