import csv
import openpyxl
import os

from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import models   

from  roles.models import UserRole
from roles.utils import can_manage_role, ROLE_HIERARCHY, has_permission
from .forms import UserEditForm, UserUploadForm, PermissionForm, PermissionGroupForm
from .models import Permission, RolePermission, PermissionGroup

from roles.decorators import permission_required

from django.http import FileResponse, HttpResponseForbidden
from django.conf import settings


# user list
@login_required
@permission_required("accounts.view_users")
def user_list(request):
    users = User.objects.select_related('role').all()

    return render(request, 'roles/user_list.html', {
        'users': users,
        'role_choices': UserRole.ROLE_CHOICES
    })

# # user detail
# @login_required
# @permission_required("accounts.edit_user")
# def user_detail(request, user_id):
#     user = get_object_or_404(User, id=user_id)
#     user_role = user.role

#     if request.method == 'POST':
#         form = UserEditForm(
#             request.POST,
#             instance=user,
#             user_role=user_role
#         )

#         if form.is_valid():
#             form.save()

#             # update role
#             new_role = form.cleaned_data['role']
#             user_role.role = new_role
#             user_role.save()

#             messages.success(request, "User updated successfully.")
#             return redirect('roles:user_detail', user_id=user.id)

#     else:
#         form = UserEditForm(
#             instance=user,
#             user_role=user_role
#         )

#     return render(request, 'roles/user_detail.html', {
#         'edit_user': user,
#         'form': form
#     })


@login_required
def user_detail(request, user_id):
    target = get_object_or_404(User, id=user_id)
    user_role = target.role

    #  Always allow viewing own profile
    if target == request.user:
        if request.method == 'POST':
            form = UserEditForm(
                request.POST,
                instance=target,
                user_role=user_role
            )

            if form.is_valid():
                form.save()
                messages.success(request, "Profile updated successfully.")
                return redirect('roles:user_detail', user_id=target.id)
        else:
            form = UserEditForm(
                instance=target,
                user_role=user_role
            )

        return render(request, 'roles/user_detail.html', {
            'edit_user': target,
            'form': form
        })

    # Must have permission to view others
    if "accounts.view_users" not in request.user_perms:
        return HttpResponseForbidden("You do not have permission to view users.")

    # Must satisfy hierarchy to view/edit others
    if not can_manage_role(request.user, target.role.role):
        return HttpResponseForbidden("You cannot access this user.")

    # Editing others requires permission
    if request.method == 'POST' and "accounts.change_roles" not in request.user_perms:
        return HttpResponseForbidden("You do not have permission to modify users.")

    # ---------- NORMAL EDIT FLOW ----------
    if request.method == 'POST':
        form = UserEditForm(
            request.POST,
            instance=target,
            user_role=user_role
        )

        if form.is_valid():
            form.save()

            new_role = form.cleaned_data['role']
            user_role.role = new_role
            user_role.save()

            messages.success(request, "User updated successfully.")
            return redirect('roles:user_detail', user_id=target.id)

    else:
        form = UserEditForm(
            instance=target,
            user_role=user_role
        )

    return render(request, 'roles/user_detail.html', {
        'edit_user': target,
        'form': form
    })



# update user role
@login_required
@permission_required("accounts.change_role")
def update_user_role(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        role = request.POST.get("role")

        try:
            user = User.objects.get(id=user_id)

            # Enforce hierarchy
            if not can_manage_role(request.user, role):
                return JsonResponse({"success": False, "error": "Not allowed"}, status=403)

            user.role.role = role
            user.role.save()
            return JsonResponse({"success": True})

        except User.DoesNotExist:
            return JsonResponse({"success": False, "error": "User not found"}, status=404)

    return JsonResponse({"success": False}, status=400)



# user upload
@login_required
@permission_required("accounts.upload_users")
def user_upload(request):
    if request.method == 'POST':
        form = UserUploadForm(request.POST, request.FILES)

        if form.is_valid():
            file = request.FILES['file']

            if file.name.endswith('.csv'):
                rows = csv.DictReader(
                    file.read().decode('utf-8').splitlines()
                )

            elif file.name.endswith('.xlsx'):
                wb = openpyxl.load_workbook(file)
                sheet = wb.active
                headers = [cell.value for cell in sheet[1]]
                rows = [
                    dict(zip(headers, row))
                    for row in sheet.iter_rows(min_row=2, values_only=True)
                ]
            else:
                messages.error(request, "Unsupported file format.")
                return redirect('roles:user_upload')

            created = 0

            for row in rows:
                username = row.get('username')
                email = row.get('email')
                password = row.get('password') or 'changeme123'

                if not username:
                    continue

                if User.objects.filter(username=username).exists():
                    continue

                user = User.objects.create(
                    username=username,
                    email=email,
                    password=make_password(password),
                    is_active=True,
                )

                UserRole.objects.create(
                    user=user,
                    role='client'
                )

                created += 1

            messages.success(
                request,
                f"{created} users uploaded successfully."
            )
            return redirect('roles:user_list')

    else:
        form = UserUploadForm()

    return render(request, 'roles/user_upload.html', {
        'form': form
    })


# download template
@login_required
@permission_required("accounts.upload_users")
def download_user_template(request):
    file_path = os.path.join(
        settings.BASE_DIR,
        'roles',
        'resources',
        'user_upload_template.xlsx'
    )

    return FileResponse(
        open(file_path, 'rb'),
        as_attachment=True,
        filename='user_upload_template.xlsx'
    )



@login_required
def permissions(request):

    ROLES = ["client", "employee", "admin", "superadmin"]

    # 🔒 VIEW PERMISSIONS
    if not has_permission(request.user, "accounts.permissions.view"):
        return HttpResponseForbidden("Access denied.")

    # -------------------------
    # SOFT DELETE PERMISSION
    # -------------------------
    if request.method == "POST" and "delete_permission" in request.POST:

        if not has_permission(request.user, "accounts.permissions.delete"):
            return HttpResponseForbidden("Not allowed.")

        perm_id = request.POST.get("delete_permission")
        permission = get_object_or_404(Permission, id=perm_id)

        permission.soft_delete(request.user)
        RolePermission.objects.filter(permission=permission).update(allowed=False)

        messages.success(request, "Permission disabled successfully.")
        return redirect(request.path)

    # -------------------------
    # SAVE MATRIX
    # -------------------------
    if request.method == "POST" and "save_permissions" in request.POST:

        if not has_permission(request.user, "accounts.permissions.edit"):
            return HttpResponseForbidden("Not allowed.")

        RolePermission.objects.all().update(allowed=False)

        for role in ROLES:
            for perm_key in request.POST.getlist(f"{role}_permissions"):
                permission = Permission.objects.get(key=perm_key, is_active=True)
                RolePermission.objects.update_or_create(
                    role=role,
                    permission=permission,
                    defaults={"allowed": True},
                )

        messages.success(request, "Permissions updated.")
        return redirect(request.path)

    # -------------------------
    # FETCH DATA
    # -------------------------
    groups = PermissionGroup.objects.prefetch_related(
        models.Prefetch("permissions")
    )

    permission_matrix = {}
    for role in ROLES:
        permission_matrix[role] = set(
            RolePermission.objects.filter(
                role=role,
                allowed=True,
                permission__is_active=True
            ).values_list("permission__key", flat=True)
        )

    context = {
        "groups": groups,
        "roles": ROLES,
        "matrix": permission_matrix,
    }

    return render(request, "roles/permissions.html", context)
