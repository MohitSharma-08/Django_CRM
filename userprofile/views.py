from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from .models import Userprofile

def signup(request):

    if request.user.is_authenticated:
        return redirect('dashboard')  # or 'index'

    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            Userprofile.objects.create(user=user)

            return redirect('/log-in/')

    else:
        form = UserCreationForm()

    return render(request, 'userprofile/signup.html',
                  {
                      'form': form
                  }) 

class CustomLoginView(LoginView):
    template_name = 'userprofile/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)
