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


class Permission(models.Model):
    key = models.CharField(max_length=100, unique=True)
    label = models.CharField(max_length=200)

    def __str__(self):
        return self.label


class RolePermission(models.Model):
    role = models.CharField(
        max_length=20,
        choices=UserRole.ROLE_CHOICES
    )
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    allowed = models.BooleanField(default=False)

    class Meta:
        unique_together = ("role", "permission")
