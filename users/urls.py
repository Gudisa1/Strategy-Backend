from rest_framework.routers import DefaultRouter
from .views import (
    DepartmentViewSet,
    PermissionViewSet,
    RoleViewSet,
    UserViewSet,
    AdminCreateViewSet,
    UserDepartmentAssignmentViewSet,  # <-- new
)

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"admin", AdminCreateViewSet, basename="admin")
router.register(r"roles", RoleViewSet, basename="role")
router.register(r"permissions", PermissionViewSet, basename="permission")
router.register(r"departments", DepartmentViewSet, basename="department")
router.register(
    r"user_departments", UserDepartmentAssignmentViewSet, basename="user-department"
)

urlpatterns = router.urls
