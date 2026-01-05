from django.shortcuts import render, redirect

def index(request):
    if request.user.is_authenticated:
        if request.user.role.role != 'client':
            return redirect('dashboard')

    return render(request, 'core/index.html')


def about(request):
    return render (request, 'core/about.html')