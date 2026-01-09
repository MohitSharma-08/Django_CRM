from .models import Permission, RolePermission

ROLE_HIERARCHY = {
    "superadmin": 100,
    "admin": 80,
    "employee": 50,
    "client": 10,
}

def role_rank(role):
    return ROLE_HIERARCHY.get(role, 0)


def can_manage_role(user, target_role):
    if not user.is_authenticated or not hasattr(user, "role"):
        return False
    return role_rank(user.role.role) > role_rank(target_role)


def is_superadmin(user):
    return (
        user.is_authenticated and
        hasattr(user, 'role') and
        user.role.role == 'superadmin'
    )

def has_permission(user, permission_key):
    if not user.is_authenticated:
        return False

    if hasattr(user, "role") and user.role.role == "superadmin":
        return True

    try:
        permission = Permission.objects.get(key=permission_key, is_active=True)
    except Permission.DoesNotExist:
        return False

    return RolePermission.objects.filter(
        role=user.role.role,
        permission=permission,
        allowed=True
    ).exists()

