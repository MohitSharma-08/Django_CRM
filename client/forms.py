from django import forms
from django.core.exceptions import ValidationError
from accounts.forms import BaseStyledForm
from .models import Client

class AddClientForm(BaseStyledForm):
    class Meta:
            model = Client
            fields= ('name', "email", "description")

    def clean_email(self):
            email = self.cleaned_data['email']

            if Client.objects.filter(email = email).exists():
                raise ValidationError('A Client with this email already exists.')
            
            return email
