from django.urls import path
from . import views

urlpatterns = [
    
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('login-otp/', views.login_with_otp, name='login_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('verify-login-otp', views.verify_login_otp, name = 'verify_login_otp'),

    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),
]