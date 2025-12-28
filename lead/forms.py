from django import forms
from .models import Lead

# Base styled form
class StyledModelForm(forms.ModelForm):
    REQUIRED_IN_STEP = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        input_style = (
            "flex h-10 w-full rounded-md border border-zinc-200 bg-zinc-50 px-3 py-2 text-sm "
            "ring-offset-white placeholder:text-zinc-400 focus-visible:outline-none "
            "focus-visible:ring-2 focus-visible:ring-zinc-950 focus-visible:ring-offset-2 "
            "disabled:opacity-50"
        )

        checkbox_style = (
            "h-4 w-4 rounded border-zinc-300 text-zinc-900 focus:ring-zinc-950"
        )

        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': checkbox_style})
            else:
                field.widget.attrs.update({'class': input_style})

            field.required = name in self.REQUIRED_IN_STEP


class AddLeadForm(StyledModelForm):
    class Meta:
        model = Lead
        fields = [
            'lead_name',
            'status',
            'email',

            'first_name',
            'middle_name',
            'last_name',
            'job_title',

            'organization_name',
            'mobile_no',
            'phone',
            'website',
            'whatsapp',

            'city',
            'state',
            'country',

            'qualification_status',
            'campaign_name',

            'disabled',
            'unsubscribed',
            'blog_subscriber',
        ]

        labels = {
            'lead_name': 'Lead Name',
            'first_name': 'Contact First Name',
            'last_name': 'Contact Last Name',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        input_style = (
            "flex h-10 w-full rounded-md border border-zinc-200 bg-zinc-50 px-3 py-2 text-sm "
            "focus:outline-none focus:ring-2 focus:ring-zinc-900"
        )

        checkbox_style = "h-4 w-4 rounded border-zinc-300 text-zinc-900"

        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = checkbox_style
            else:
                field.widget.attrs['class'] = input_style




# STEP 1 – Basic Info
class LeadStep1Form(StyledModelForm):
    REQUIRED_IN_STEP = ['first_name','lead_name']

    class Meta:
        model = Lead
        fields = [
            'lead_name',
            'status',
            'email',
            'first_name',
            'last_name',
            'source',
            'lead_type',
        ]
        labels = {
            'lead_name': 'Lead Name',
            'first_name': 'Contact First Name',
            'last_name': 'Contact Last Name',
        }


# STEP 2 – Contact Info
class LeadStep2Form(StyledModelForm):
    REQUIRED_IN_STEP = []

    class Meta:
        model = Lead
        fields = [
            'email',
            'mobile_no',
            'phone',
            'website',
            'whatsapp',
            'phone_ext',
        ]


# STEP 3 – Organization
class LeadStep3Form(StyledModelForm):
    REQUIRED_IN_STEP = []

    class Meta:
        model = Lead
        fields = [
            'organization_name',
            'annual_revenue',
            'territory',
            'no_of_employees',
            'industry',
            'fax',
            'market_segment',
        ]


# STEP 4 – Address
class LeadStep4Form(StyledModelForm):
    REQUIRED_IN_STEP = []

    class Meta:
        model = Lead
        fields = [
            'city',
            'state',
            'country',
        ]


# STEP 5 – Qualification & Extras
class LeadStep5Form(StyledModelForm):
    REQUIRED_IN_STEP = []

    class Meta:
        model = Lead
        fields = [
            'qualification_status',
            'qualified_by',
            'qualified_on',
            'campaign_name',
            'print_language',
            'disabled',
            'unsubscribed',
            'blog_subscriber',
        ]


# Upload form (unchanged)
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
