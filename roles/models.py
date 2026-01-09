# roles/models.py
from django.db import models
from django.contrib.auth.models import User


class UserRole(models.Model):

    ROLE_CHOICES = (
        ('superadmin', 'Super Admin'),
        ('admin', 'Admin'),
        ('employee', 'Employee'),
        ('client', 'Client'),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='role'
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='client'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} → {self.role}"



class PermissionGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Permission(models.Model):
    key = models.CharField(max_length=100, unique=True)
    label = models.CharField(max_length=200)
    group = models.ForeignKey(
        PermissionGroup,
        on_delete=models.CASCADE,
        related_name="permissions",
    )

    # 🔐 SOFT DELETE FIELDS
    is_active = models.BooleanField(default=True)
    deleted_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="deleted_permissions"
    )
    deleted_by_role = models.CharField(max_length=50, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def soft_delete(self, user):
        from django.utils import timezone

        self.is_active = False
        self.deleted_by = user
        self.deleted_by_role = user.role.role if hasattr(user, "role") else None
        self.deleted_at = timezone.now()
        self.save()



class RolePermission(models.Model):
    role = models.CharField(
        max_length=20,
        choices=UserRole.ROLE_CHOICES
    )
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    allowed = models.BooleanField(default=False)

    class Meta:
        unique_together = ("role", "permission")

