from django import template
from roles.utils import has_permission

register = template.Library()

@register.simple_tag(takes_context=True)
def has_perm(context, permission_key):
    request = context.get("request")
    if not request:
        return False
    return has_permission(request.user, permission_key)
