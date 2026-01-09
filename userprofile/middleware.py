from django.shortcuts import redirect
from django.urls import reverse

class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Prevent logged-in users from visiting auth pages
        auth_urls = [
            reverse('login'), 
            reverse('login_otp'), 
            reverse('signup'), 
            reverse('forgot_password')
        ]
        
        if request.user.is_authenticated and request.path in auth_urls:
            from .utils import redirect_by_role
            return redirect(redirect_by_role(request.user))

        response = self.get_response(request)

        # 2. Kill the browser cache for all responses
        # This is what makes the "Back" button work correctly
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        
        return response