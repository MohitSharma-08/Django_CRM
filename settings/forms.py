from django import forms
from .models import AppSetting

class AppSettingForm(forms.ModelForm):
    class Meta:
        model = AppSetting
        fields = ['app_name', 'logo', 'base_url']
