from django.db import models
import uuid
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError("Users must have a username")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        if password:
            user.set_password(password)  # hashes password properly
        else:
            raise ValueError("Users must have a password")
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_sys_admin", True)  # Sys Admin by default
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_sys_admin = models.BooleanField(default=False)

    role = models.ForeignKey(
        "Role", on_delete=models.SET_NULL, null=True, blank=True, related_name="users"
    )
    departments = models.ManyToManyField("Department", related_name="users", blank=True)
    permissions = models.ManyToManyField("Permission", related_name="users", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def get_all_roles(self):
        roles = set()
        if self.role:
            roles.add(self.role)
        for department in self.departments.all():
            for role in department.roles.all():
                roles.add(role)
        return roles

    def get_all_permissions(self, obj=...):
        permissions = set()
        for role in self.get_all_roles():
            for permission in role.permissions.all():
                permissions.add(permission.name)
        return permissions

    def __str__(self):
        return self.username


class Permission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Role(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    permissions = models.ManyToManyField("Permission", related_name="roles", blank=True)

    def __str__(self):
        return self.name


class Department(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    roles = models.ManyToManyField("Role", related_name="departments", blank=True)

    def __str__(self):
        return self.name
