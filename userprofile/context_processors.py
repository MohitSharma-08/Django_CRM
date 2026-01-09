def sidebar_visibility(request):
    """
    Determines if the sidebar/navbar (app shell) should be visible.
    """
    # 1. Define pages where the sidebar should NEVER appear
    auth_pages = [
        'login', 
        'signup', 
        'login_otp', 
        'verify_login_otp', 
        'forgot_password', 
        'verify_otp', 
        'reset_password'
    ]

    # 2. Get the name of the current URL
    current_url_name = request.resolver_match.url_name if request.resolver_match else None

    # 3. Logic: User must be logged in AND not on an auth page
    show_shell = request.user.is_authenticated and current_url_name not in auth_pages

    return {
        'show_app_shell': show_shell
    }