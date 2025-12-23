from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import AccountProfile


@login_required
def profile(request):
    user = request.user
    profile, _ = AccountProfile.objects.get_or_create(user=user)

    if request.method == "POST":

        user.username = request.POST.get("username", user.username)
        user.email = request.POST.get("email", user.email)

        if request.FILES.get("avatar"):
            profile.avatar = request.FILES["avatar"]

        # PASSWORD CHANGE (SECURE)
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if new_password:
            if not user.check_password(old_password):
                messages.error(request, "Old password is incorrect.")
                return redirect("profile")

            if new_password != confirm_password:
                messages.error(request, "New passwords do not match.")
                return redirect("profile")

            user.set_password(new_password)
            update_session_auth_hash(request, user)

        user.save()
        profile.save()

        messages.success(request, "Profile updated successfully.")
        return redirect("profile")

    return render(request, "useraccount/profile.html")
