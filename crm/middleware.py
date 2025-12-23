from django.shortcuts import redirect

class RedirectAuthenticatedUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if request.resolver_match and request.resolver_match.url_name in ["login", "signup"]:
                return redirect("dashboard")

        return self.get_response(request)
