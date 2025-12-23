from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text="Required. Informative only."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        shadcn_classes = (
            "flex h-10 w-full rounded-md border border-zinc-200 bg-white px-3 py-2 text-sm "
            "ring-offset-white file:border-0 file:bg-transparent file:text-sm file:font-medium "
            "placeholder:text-zinc-500 focus-visible:outline-none focus-visible:ring-2 "
            "focus-visible:ring-zinc-950 focus-visible:ring-offset-2 disabled:cursor-not-allowed "
            "disabled:opacity-50 transition-all outline-none"
        )
        
        for field_name, field in self.fields.items():
            # Add the CSS classes
            field.widget.attrs.update({'class': shadcn_classes})
            
            # Safely set the placeholder
            if field.label:
                field.widget.attrs.update({'placeholder': f"Enter your {field.label.lower()}"})
            else:
                # Fallback placeholder if label is missing
                field.widget.attrs.update({'placeholder': f"Enter {field_name.replace('_', ' ')}"})

    class Meta:
        model = User
        fields = ('username', 'email') # password1 and password2 are included by UserCreationForm

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user