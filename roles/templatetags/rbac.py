from django import template
from roles.utils import can_manage_role as _can_manage_role

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def has_any(user_perms, perm_list):
    """
    Usage:
    {% if request.user_perms|has_any:"leads.view,leads.create" %}
    """
    if not user_perms:
        return False

    perms = [p.strip() for p in perm_list.split(",")]
    return any(p in user_perms for p in perms)

@register.filter
def can_manage_role(user, role):
    return _can_manage_role(user, role)
