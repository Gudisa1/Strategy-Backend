from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .models import User, Department, Role, Permission

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from rest_framework import exceptions

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom serializer to allow both normal users and superusers to obtain tokens.
    """
    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        if username is None or password is None:
            raise exceptions.AuthenticationFailed("Username and password are required.")

        # Authenticate user
        user = authenticate(username=username, password=password)
        print("Authenticated user:", user)

        if user is None:
            raise exceptions.AuthenticationFailed("Invalid username or password.")

        if not user.is_active:
            raise exceptions.AuthenticationFailed("User account is inactive.")

        # Return token pair
        data = super().validate(attrs)
        return data


# Small serializers for nested objects
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name"]


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name"]


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["id", "name"]


class UserSerializer(serializers.ModelSerializer):
    # Read: nested serializers
    role = RoleSerializer(read_only=True)
    departments = DepartmentSerializer(read_only=True, many=True)
    permissions = PermissionSerializer(read_only=True, many=True)

    # Write: accept names instead of IDs
    role_name = serializers.SlugRelatedField(
        queryset=Role.objects.all(),
        slug_field="name",
        source="role",
        write_only=True,
        required=False,
    )
    department_names = serializers.SlugRelatedField(
        queryset=Department.objects.all(),
        many=True,
        slug_field="name",
        source="departments",
        write_only=True,
        required=False,
    )
    permission_names = serializers.SlugRelatedField(
        queryset=Permission.objects.all(),
        many=True,
        slug_field="name",
        source="permissions",
        write_only=True,
        required=False,
    )

    password = serializers.CharField(write_only=True, required=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "phone_number",
            "email",
            "password",
            "is_active",
            "is_staff",
            "is_sys_admin",
            "role",             # read: {id, name}
            "role_name",        # write: "Admin"
            "departments",      # read: [{id, name}, ...]
            "department_names", # write: ["Finance", "HR"]
            "permissions",      # read: [{id, name}, ...]
            "permission_names", # write: ["Add User", "Delete User"]
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        # Extract nested write-only fields
        role = validated_data.pop("role", None)
        departments = validated_data.pop("departments", [])
        permissions = validated_data.pop("permissions", [])
        
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)  # Hash the password
        if role:
            user.role = role
        user.save()

        if departments:
            user.departments.set(departments)
        if permissions:
            user.permissions.set(permissions)

        return user

    def update(self, instance, validated_data):
        # Handle password update
        password = validated_data.pop("password", None)
        if password:
            instance.set_password(password)

        # Handle nested fields
        role = validated_data.pop("role", None)
        departments = validated_data.pop("departments", None)
        permissions = validated_data.pop("permissions", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if role is not None:
            instance.role = role
        if departments is not None:
            instance.departments.set(departments)
        if permissions is not None:
            instance.permissions.set(permissions)

        instance.save()
        return instance


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["id", "name", "description"]


class RoleSerializer(serializers.ModelSerializer):
    # Read: show permissions as {id, name}
    permissions = PermissionSerializer(many=True, read_only=True)

    # Write: accept permissions by name
    permission_names = serializers.SlugRelatedField(
        many=True,
        slug_field="name",   # lookup by name instead of ID
        queryset=Permission.objects.all(),
        source="permissions",
        write_only=True
    )

    class Meta:
        model = Role
        fields = ["id", "name", "description", "permissions", "permission_names"]


class DepartmentSerializer(serializers.ModelSerializer):
    # Read: show roles as objects with id + name
    roles = RoleSerializer(many=True, read_only=True)

    # Write: accept role names instead of IDs
    role_names = serializers.SlugRelatedField(
        queryset=Role.objects.all(),
        many=True,
        slug_field="name",   # lookup by name
        source="roles",
        write_only=True
    )

    class Meta:
        model = Department
        fields = ["id", "name", "description", "roles", "role_names"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        roles = validated_data.pop("roles", [])
        department = Department.objects.create(**validated_data)
        if roles:
            department.roles.set(roles)
        return department

    def update(self, instance, validated_data):
        roles = validated_data.pop("roles", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if roles is not None:
            instance.roles.set(roles)

        return instance



class UserDepartmentAssignmentSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField()
    department_id = serializers.UUIDField()

    class Meta:
        model = User.departments.through  # this is the auto M2M table
        fields = ["id", "user_id", "department_id", "user", "department"]
        read_only_fields = ["id", "user", "department"]

    def validate(self, data):
        from django.core.exceptions import ObjectDoesNotExist

        try:
            data["user"] = User.objects.get(id=data["user_id"])
        except ObjectDoesNotExist:
            raise serializers.ValidationError({"user_id": "User does not exist"})

        try:
            data["department"] = Department.objects.get(id=data["department_id"])

        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                {"department_id": "Department does not exist"}
            )

        return data

    def create(self, validated_data):
        user = validated_data["user"]
        department = validated_data["department"]
        user.departments.add(department)
        return {
            "user_id": str(user.id),
            "department_id": str(department.id),
            "user": str(user),
            "department": str(department),
        }

    def remove(self):
        """
        Remove the department from the user.
        """
        user = self.validated_data["user"]
        department = self.validated_data["department"]
        user.departments.remove(department)
        return {
            "user_id": str(user.id),
            "department_id": str(department.id),
            "user": str(user),
            "department": str(department),
        }
