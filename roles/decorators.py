from functools import wraps
from django.http import HttpResponseForbidden
from .utils import has_permission

def permission_required(permission_key):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not has_permission(request.user, permission_key):
                return HttpResponseForbidden("Access denied.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
