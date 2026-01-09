from django.contrib import admin
from .models import Permission

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("key", "label", "is_active", "deleted_by", "deleted_by_role", "deleted_at")
    list_filter = ("is_active", "group")
