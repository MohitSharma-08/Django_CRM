from .models import Permission, RolePermission

def is_superadmin(user):
    return (
        user.is_authenticated and
        hasattr(user, 'role') and
        user.role.role == 'superadmin'
    )

def has_permission(user, permission_key):
    """
    Check if user has a specific permission
    """
    if not user.is_authenticated:
        return False

    # Superadmin = full access
    if hasattr(user, "role") and user.role.role == "superadmin":
        return True

    try:
        permission = Permission.objects.get(key=permission_key)
    except Permission.DoesNotExist:
        return False

    return RolePermission.objects.filter(
        role=user.role.role,
        permission=permission,
        allowed=True
    ).exists()
