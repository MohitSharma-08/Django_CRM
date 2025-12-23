from django import forms
from accounts.forms import BaseStyledForm
from .models import Lead

class AddLeadForm(BaseStyledForm):
    class Meta:
        model = Lead
        fields= ('name', "email", "description", "priority", "status")


class LeadUploadForm(forms.Form):
    file = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'class': (
                'block w-full text-sm text-gray-700 '
                'file:mr-4 file:py-2 file:px-4 '
                'file:rounded-lg file:border-0 '
                'file:text-sm file:font-semibold '
                'file:bg-teal-50 file:text-teal-700 '
                'hover:file:bg-teal-100'
            )
        })
    )
