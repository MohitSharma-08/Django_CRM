from roles.models import RolePermission, Permission

class PermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.user_perms = set()
        request.sidebar = {
            "leads": False,
            "pipeline": False,
            "clients": False,
            "roles": False,
            "settings": False,
        }
        request.show_app_shell = False

        if not request.user.is_authenticated or not hasattr(request.user, "role"):
            return self.get_response(request)

        role = request.user.role.role

        # -----------------------------------
        # SUPERADMIN = FULL ACCESS
        # -----------------------------------
        if role == "superadmin":
            perms = set(
                Permission.objects.values_list("key", flat=True)
            )

            request.user_perms = perms
            request.sidebar = {
                "leads": True,
                "pipeline": True,
                "clients": True,
                "roles": True,
                "settings": True,
            }
            request.show_app_shell = True
            return self.get_response(request)

        # -----------------------------------
        # NORMAL ROLES
        # -----------------------------------
        perms = set(
            RolePermission.objects.filter(
                role=role,
                allowed=True
            ).values_list("permission__key", flat=True)
        )

        request.user_perms = perms

        request.sidebar["leads"] = "leads.view" in perms
        request.sidebar["pipeline"] = "leads.view" in perms
        request.sidebar["clients"] = "clients.view" in perms
        request.sidebar["roles"] = any(p.startswith("accounts.") for p in perms)
        request.sidebar["settings"] = any(p.startswith("settings.") for p in perms)


        request.show_app_shell = any(request.sidebar.values())

        return self.get_response(request)
