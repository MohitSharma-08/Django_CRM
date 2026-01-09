# core/views.py
from django.shortcuts import render, redirect

def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    return render(request, 'core/index.html')


def about(request):
    return render(request, 'core/about.html')

