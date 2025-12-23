from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import AppSetting

@login_required
def app_settings(request):
    app_setting, _ = AppSetting.objects.get_or_create(id=1)

    if request.method == "POST":

        # BASIC APP SETTINGS
        app_setting.app_name = request.POST.get("app_name", app_setting.app_name)

        base_url = request.POST.get("base_url")
        app_setting.base_url = base_url if base_url else request.build_absolute_uri("/")[:-1]

        # LOGO HANDLING
        remove_logo = request.POST.get("remove_logo") == "true"

        if remove_logo and app_setting.logo:
            app_setting.logo.delete(save=False)
            app_setting.logo = None

        if request.FILES.get("logo"):
            app_setting.logo = request.FILES["logo"]

        # SMTP SETTINGS
        app_setting.smtp_host = request.POST.get("smtp_host", "")
        app_setting.smtp_port = request.POST.get("smtp_port") or 587
        app_setting.smtp_username = request.POST.get("smtp_username", "")
        app_setting.smtp_password = request.POST.get("smtp_password", "")
        app_setting.smtp_use_tls = bool(request.POST.get("smtp_use_tls"))
        app_setting.smtp_use_ssl = bool(request.POST.get("smtp_use_ssl"))
        app_setting.smtp_from_email = request.POST.get("smtp_from_email", "")

        app_setting.save()

        messages.success(request, "Application settings updated successfully.")
        return redirect("app_settings")

    return render(request, "settings/app_settings.html", {
        "settings": app_setting
    })
