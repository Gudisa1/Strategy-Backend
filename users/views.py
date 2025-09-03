from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from .models import Department, Permission, User, Role
from .serializers import (
    DepartmentSerializer,
    PermissionSerializer,
    UserDepartmentAssignmentSerializer,
    UserSerializer,
    RoleSerializer,
)
from .permissions import IsSysAdminOrSelf
from users import permissions
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.authentication import JWTAuthentication


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsSysAdminOrSelf]
    authentication_classes = [JWTAuthentication]  # Add this line

    def get_queryset(self):
        user = self.request.user
        if user.is_sys_admin:
            return User.objects.all()
        return User.objects.filter(id=user.id)

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        self.perform_destroy(user)
        return Response(
            {"detail": f"User '{user.username}' has been deleted successfully."},
            status=status.HTTP_200_OK,
        )


class AdminCreateViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"])
    @csrf_exempt
    def create_admin(self, request):
        if not request.user.is_sys_admin:
            return Response(
                {"detail": "Only sys admins can create admin users."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(
                is_staff=False, is_superuser=False, is_sys_admin=True
            )
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, IsSysAdminOrSelf]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSysAdminOrSelf()]
        return [permissions.IsSysAdminOrSelf()]


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, IsSysAdminOrSelf]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSysAdminOrSelf()]
        return [permissions.IsSysAdminOrSelf()]


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, IsSysAdminOrSelf]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSysAdminOrSelf()]
        return [permissions.IsSysAdminOrSelf()]


class UserDepartmentAssignmentViewSet(viewsets.ViewSet):
    serializer_class = UserDepartmentAssignmentSerializer

    permission_classes = [IsSysAdminOrSelf]

    def get_permissions(self):
        if self.action in ["create", "destroy"]:
            return [IsSysAdminOrSelf()]
        return super().get_permissions()

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(result, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.remove()
        return Response(result, status=status.HTTP_204_NO_CONTENT)

    def list(self, request):
        user_id = request.query_params.get("user_id")
        if not user_id:
            return Response({"error": "user_id query parameter required"}, status=400)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        departments = user.departments.all()
        data = [
            {"id": str(d.id), "name": d.name, "description": d.description}
            for d in departments
        ]
        return Response(data, status=status.HTTP_200_OK)
