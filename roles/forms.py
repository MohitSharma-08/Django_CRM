from django import forms
from django.contrib.auth.models import User
from .models import UserRole


class UserEditForm(forms.ModelForm):
    role = forms.ChoiceField(choices=UserRole.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email', 'is_active']

    def __init__(self, *args, **kwargs):
        user_role = kwargs.pop('user_role', None)
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update({
            'class': 'input'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'input'
        })
        self.fields['is_active'].widget.attrs.update({
            'class': 'h-4 w-4'
        })
        self.fields['role'].widget.attrs.update({
            'class': 'input'
        })

        if user_role:
            self.fields['role'].initial = user_role.role


class UserUploadForm(forms.Form):
    file = forms.FileField()
