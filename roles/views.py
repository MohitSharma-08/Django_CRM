import csv
import openpyxl

from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.models import User

from  roles.models import UserRole
from .forms import UserEditForm, UserUploadForm
from .models import Permission, RolePermission

from django.http import FileResponse, HttpResponseForbidden
from django.conf import settings
import os


@login_required
def user_list(request):
    if request.user.role.role != 'superadmin':
        return HttpResponseForbidden()

    users = User.objects.select_related('role').all()

    return render(request, 'roles/user_list.html', {
        'users': users,
        'role_choices': UserRole.ROLE_CHOICES
    })


@login_required
def user_detail(request, user_id):
    if request.user.role.role != 'superadmin':
        return HttpResponseForbidden()

    user = get_object_or_404(User, id=user_id)
    user_role = user.role

    if request.method == 'POST':
        form = UserEditForm(
            request.POST,
            instance=user,
            user_role=user_role
        )

        if form.is_valid():
            form.save()

            # update role
            new_role = form.cleaned_data['role']
            user_role.role = new_role
            user_role.save()

            messages.success(request, "User updated successfully.")
            return redirect('roles:user_detail', user_id=user.id)

    else:
        form = UserEditForm(
            instance=user,
            user_role=user_role
        )

    return render(request, 'roles/user_detail.html', {
        'edit_user': user,
        'form': form
    })


from django.views.decorators.http import require_POST
from django.http import JsonResponse

# @require_POST
# @login_required
# def update_user_role(request):
#     if request.user.role.role != 'superadmin':
#         return JsonResponse({'error': 'Forbidden'}, status=403)

#     user_id = request.POST.get('user_id')
#     role = request.POST.get('role')

#     try:
#         user = User.objects.get(id=user_id)
#         user.role.role = role
#         user.role.save()
#         return JsonResponse({'success': True})
#     except User.DoesNotExist:
#         return JsonResponse({'error': 'User not found'}, status=404)

@login_required
def update_user_role(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        role = request.POST.get("role")

        try:
            user = User.objects.get(id=user_id)
            user.role.role = role
            user.role.save()
            return JsonResponse({"success": True})
        except Exception:
            return JsonResponse({"success": False})

    return JsonResponse({"success": False})


@login_required
def user_upload(request):
    if request.user.role.role != 'superadmin':
        return HttpResponseForbidden()

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



@login_required
def download_user_template(request):
    if request.user.role.role != 'superadmin':
        return HttpResponseForbidden()

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

# roles/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Permission, RolePermission, UserRole


@login_required
def permissions(request):

    PERMISSION_GROUPS = {
        "Leads": [
            ("leads.create", "Create"),
            ("leads.view", "View"),
            ("leads.edit", "Edit"),
            ("leads.delete", "Delete"),
            ("leads.upload", "Upload"),
            ("leads.convert", "Convert → Client"),
        ],
        "Clients": [
            ("clients.create", "Create"),
            ("clients.view", "View"),
            ("clients.edit", "Edit"),
            ("clients.delete", "Delete"),
            ("clients.upload", "Upload"),
        ],
        "Accounts & Users": [
            ("accounts.view_users", "View Users"),
            ("accounts.change_roles", "Change Roles"),
            ("accounts.deactivate_users", "Activate / Deactivate Users"),
        ],
        "System Settings": [
            ("settings.branding", "Branding"),
            ("settings.smtp", "SMTP / Email"),
            ("settings.urls", "Main URLs"),
            ("settings.integrations", "Integrations"),
            ("settings.configs", "Global Configs"),
        ],
    }

    ROLES = ["admin", "employee", "client", "superadmin"]

    # Create Permission rows if missing
    for group in PERMISSION_GROUPS.values():
        for key, label in group:
            Permission.objects.get_or_create(
                key=key,
                defaults={"label": label},
            )

    if request.method == "POST":
        RolePermission.objects.all().update(allowed=False)

        for role in ROLES:
            for perm_key in request.POST.getlist(f"{role}_permissions"):
                permission = Permission.objects.get(key=perm_key)
                RolePermission.objects.update_or_create(
                    role=role,
                    permission=permission,
                    defaults={"allowed": True},
                )

        return redirect(request.path)

    # Build permission matrix
    permission_matrix = {}

    for role in ROLES:
        permission_matrix[role] = set(
            RolePermission.objects.filter(
                role=role,
                allowed=True
            ).values_list("permission__key", flat=True)
        )

    context = {
        "permission_groups": PERMISSION_GROUPS,
        "roles": ROLES,
        "matrix": permission_matrix,
    }

    return render(request, "roles/permissions.html", context)
