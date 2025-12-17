from django import forms
from accounts.forms import BaseStyledForm
from .models import Client

class AddClientForm(BaseStyledForm):
    class Meta:
        model = Client
        fields= ('name', "email", "description")