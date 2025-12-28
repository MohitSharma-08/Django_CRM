from django.shortcuts import render, redirect

def index(request):
    # Optional: If the user is already logged in, redirect them straight to the dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    # Otherwise, show the landing page
    return render(request, 'core/index.html')

def about(request):
    return render (request, 'core/about.html')