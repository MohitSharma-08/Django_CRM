import random

from django.utils import timezone
from django.http import JsonResponse
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages

from .forms import CustomUserCreationForm
from .models import Userprofile

from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache


@never_cache
def signup(request):

    if request.user.is_authenticated:
        return redirect('dashboard')  # or 'index'

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user= form.save()

            Userprofile.objects.create(user=user)

            login(request, user)

            messages.success(request, f"Welocme, {user.username}!")
            return redirect('dashboard')

    else:
        form = CustomUserCreationForm()

    return render(request, 'userprofile/signup.html',
                  {
                      'form': form
                  }) 


# Authentication (login)
class CustomLoginView(LoginView):
    template_name = 'userprofile/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)
    
# otp login
def login_with_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        if not email:
            messages.error(request, "Email is required")
            return redirect('login_otp')

        try: 
            user = User.objects.get(email = email)
        except User.DoesNotExist:
            messages.error(request, "No sccount with this email.")
            return redirect('login_otp')
        
        otp = str(random.randint(100000,999999))

        profile = user.userprofile 
        profile.otp = otp 
        profile.otp_created_at = timezone.now()
        profile.save()

        send_mail(
            'Your login OTP',
            f'Your OTP is {otp}. Valid for 5 minutes.',
            None,
            [email],
            fail_silently=False
        )

        request.session['login_otp_email'] = email
        return redirect('verify_login_otp')

    return render(request, 'userprofile/login_otp.html')



# Verify OTP and Login User
@never_cache
def verify_login_otp(request):
    email = request.session.get('login_otp_email')

    if not email:
        return redirect('login_otp')
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return redirect('login_otp')
    
    profile = user.userprofile

    if request.method == 'POST':
        otp_input = request.POST.get('otp')

        if profile.otp == otp_input and profile.is_otp_valid():
            login(request, user)

            # clear OTP
            profile.otp = None
            profile.otp_created_at = None
            profile.save()

            del request.session['login_otp_email']

            return redirect('dashboard')

        else:
            messages.error(request, "Invalid or expired OTP.")

    return render(request, 'userprofile/verify_login_otp.html')





#  forgot password 

@never_cache
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)

            otp = str(random.randint(100000, 999999))

            profile = user.userprofile
            profile.otp = otp
            profile.otp_created_at = timezone.now()
            profile.save()

            send_mail(
                'Your Password Reset OTP',
                f'Your otp is {otp}. It expires in 10 minutes.',
                'no-reply@teal-crm.com',
                [email],
                fail_silently=False
            )

            request.session['reset_email'] = email 
            return redirect('verify_otp')
        
        except User.DoesNotExist:
            messages.error(request, "No user with this email.")
    
    return render(request, 'userprofile/forgot_password.html')


@never_cache
def verify_otp(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('forgot_password')

    if request.method == 'POST':
        otp_input = request.POST.get('otp')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return redirect('forgot_password')

        profile = user.userprofile

        if profile.otp == otp_input and profile.is_otp_valid():
            return redirect('reset_password')
        else:
            messages.error(request, "Invalid or expired OTP.")

    return render(request, 'userprofile/verify_otp.html')

@never_cache
def reset_password(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('forgot_password')

    if request.method == 'POST':
        p1 = request.POST.get('pass1')
        p2 = request.POST.get('pass2')

        if p1 != p2:
            messages.error(request, "Passwords do not match")
            return redirect('reset_password')

        user = User.objects.get(email=email)
        user.set_password(p1)
        user.save()

        profile = user.userprofile
        profile.otp = None
        profile.otp_created_at = None
        profile.save()

        del request.session['reset_email']

        messages.success(request, "Password reset successful")
        return redirect('login')

    return render(request, 'userprofile/reset_password.html')



def resend_otp(request):
    email = request.session.get('login_otp_email')

    if not email :
        return JsonResponse({'status': 'error', 'message': 'session expired'}, status = 400)
    
    try: 
        user = User.objects.get( email = email)
        otp = str(random.randint(100000,999999))

        profile = user.userprofile
        profile.otp = otp
        profile.otp_created_at = timezone.now()
        profile.save()

        send_mail(
            'Your new OTP',
            f'Your new OTP is {otp}.',
            None,
            [email],
            fail_silently=False
        )
        return JsonResponse({'status': 'success'})
    except Exception:
        return JsonResponse({'status': 'error'}, status=500 )