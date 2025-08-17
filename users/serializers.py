from rest_framework import serializers
from .models import User, Department, Role, Permission


class UserSerializer(serializers.ModelSerializer):
    departments = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), many=True, required=False
    )
    password = serializers.CharField(write_only=True, required=False, min_length=8)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "is_active",
            "is_staff",
            "is_sys_admin",
            "departments",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        departments = validated_data.pop("departments", [])
        password = validated_data.pop("password", None)

        if not password:
            raise serializers.ValidationError({"password": "Password is required."})
        user = User.objects.create_user(password=password, **validated_data)

        user.departments.set(departments)
        return user

    def update(self, instance, validated_data):
        departments = validated_data.pop("departments", None)
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()

        if departments is not None:
            instance.departments.set(departments)

        return instance


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["id", "name", "description"]


class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    permissions_ids = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True,
        write_only=True,
        source="permissions",
    )

    class Meta:
        model = Role
        fields = ["id", "name", "description", "permissions", "permissions_ids"]


class DepartmentSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(many=True, read_only=True)

    role_ids = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        many=True,
        write_only=True,
        source="roles",
    )

    class Meta:
        model = Department
        fields = ["id", "name", "description", "roles", "role_ids"]
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
