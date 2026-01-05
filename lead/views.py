import json
import pandas as pd

from django.http import HttpResponse
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from client.models import Client

from roles.decorators import has_permission
from roles.utils import has_permission

from .models import Lead
from .forms import AddLeadForm
from .forms import LeadUploadForm
from .forms import (
    LeadStep1Form, LeadStep2Form, LeadStep3Form,
    LeadStep4Form, LeadStep5Form
)

STEPS = {
    1: LeadStep1Form,
    2: LeadStep2Form,
    3: LeadStep3Form,
    4: LeadStep4Form,
    5: LeadStep5Form,
}

STEPPER_LABELS = [
    "Create",
    "Contact",
    "Organization",
    "Address",
    "Qualify",
]

@login_required
def lead_wizard(request, step=1, pk=None):
    step = int(step)

    STEPS = {
        1: LeadStep1Form,
        2: LeadStep2Form,
        3: LeadStep3Form,
        4: LeadStep4Form,
        5: LeadStep5Form,
    }

    STEP_TITLES = {
        1: "Lead Details",
        2: "Contact Person",
        3: "Contact Information",
        4: "Organization & Address",
        5: "Qualification & Assignment",
    }

    total_steps = len(STEPS)
    session_key = f"lead_wizard_{pk or 'new'}"
    instance = None

    # ---------- EDIT MODE ----------
    if pk:
        instance = get_object_or_404(
            Lead,
            pk=pk,
            lead_owner=request.user,
            deleted_at__isnull=True
        )

        if session_key not in request.session:
            request.session[session_key] = {}
            for field in Lead._meta.fields:
                if field.name in ['id', 'created_at', 'modified_at']:
                    continue
                value = getattr(instance, field.name)
                if field.is_relation:
                    value = value.id if value else None
                request.session[session_key][field.name] = value

    session_data = request.session.get(session_key, {})
    form_class = STEPS[step]

    # ---------- POST ----------
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            session_data.update(form.cleaned_data)
            request.session[session_key] = session_data

            if step < total_steps:
                if pk:
                    return redirect('edit_lead_step', pk=pk, step=step + 1)
                else:
                    return redirect('add_lead_step', step=step + 1)

            # FINAL SAVE
            if instance:
                for key, value in session_data.items():
                    field = Lead._meta.get_field(key)
                    if field.is_relation:
                        setattr(instance, f"{key}_id", value)
                    else:
                        setattr(instance, key, value)
                instance.save()
            else:
                Lead.objects.create(
                    **session_data,
                    lead_owner=request.user
                )

            request.session.pop(session_key, None)
            messages.success(request, "Lead saved successfully")
            return redirect('leads_list')

    # ---------- GET ----------
    else:
        form = form_class(initial=session_data)

    progress_percent = int((step - 1) / (total_steps - 1) * 100)

    return render(request, 'lead/add_lead.html', {
        'form': form,
        'step': step,
        'total_steps': total_steps,
        'step_title': STEP_TITLES[step],
        'stepper_labels': STEPPER_LABELS,
        'progress_percent': progress_percent,
        'is_edit': bool(pk),
    })



@login_required
def leads_list(request):
    leads = Lead.objects.filter(
        lead_owner=request.user,
        deleted_at__isnull=True,
        converted_to_client=False
    )

    paginator = Paginator(leads, 10)
    page_number = request.GET.get('page')
    leads_page = paginator.get_page(page_number)

    return render(request, 'lead/leads_list.html', {
        'leads': leads_page
    })


@login_required
def leads_detail(request, pk):
    lead = get_object_or_404(
        Lead,
        pk=pk,
        lead_owner=request.user,
        deleted_at__isnull=True
    )

    return render(request, 'lead/leads_details.html', {
        'lead': lead
    })


@login_required
def leads_delete(request, pk):
    lead = get_object_or_404(
        Lead,
        pk=pk,
        lead_owner=request.user
    )

    if request.method == 'POST':
        lead.deleted_at = timezone.now()
        lead.deleted_by = request.user
        lead.save()
        messages.success(request, 'Lead deleted successfully')

    return redirect('leads_list')


@login_required
def leads_edit(request, pk):
    lead = get_object_or_404(
        Lead,
        pk=pk,
        lead_owner=request.user
    )

    if request.method == 'POST':
        form = AddLeadForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            messages.success(request, "Changes applied.")
            return redirect('leads_list')
    else:
        form = AddLeadForm(instance=lead)

    return render(request, 'lead/leads_edit.html', {
        'form': form
    })


@login_required
def add_lead(request, step=1):
    step = int(step)
    form_class = STEPS[step]

    STEP_TITLES = {
        1: "Lead Details",
        2: "Contact Person",
        3: "Contact Information",
        4: "Organization & Address",
        5: "Qualification & Assignment",
    }

    total_steps = len(STEPS)
    session_data = request.session.get('lead_form', {})

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            session_data.update(form.cleaned_data)
            request.session['lead_form'] = session_data

            if step < total_steps:
                return redirect('add_lead_step', step=step + 1)

            Lead.objects.create(
                **session_data,
                lead_owner=request.user
            )

            request.session.pop('lead_form')
            messages.success(request, 'Lead created successfully.')
            return redirect('leads_list')
    else:
        form = form_class(initial=session_data)

    progress_percent = int((step - 1) / (total_steps - 1) * 100)

    return render(request, 'lead/add_lead.html', {
        'form': form,
        'step': step,
        'total_steps': total_steps,
        'step_title': STEP_TITLES[step],
        'stepper_labels': STEPPER_LABELS,
        'progress_percent': progress_percent,
    })



@login_required
def convert_to_client(request, pk):
    lead = get_object_or_404(
        Lead,
        pk=pk,
        lead_owner=request.user
    )

    Client.objects.create(
        name=lead.first_name,
        email=lead.email,
        created_by=request.user
    )

    lead.converted_to_client = True
    lead.save()

    messages.success(request, 'The lead was successfully converted to a client.')
    return redirect('leads_list')


@login_required
def upload_leads(request):
    if request.method == 'POST':
        form = LeadUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']

            try:
                if file.name.endswith('.csv'):
                    df = pd.read_csv(file)
                elif file.name.endswith('.xlsx'):
                    df = pd.read_excel(file)
                else:
                    messages.error(request, 'Unsupported file format.')
                    return redirect('leads_list')

                df.columns = df.columns.str.lower()

                required_columns = {'name', 'email'}
                if not required_columns.issubset(df.columns):
                    messages.error(request, 'File has missing required columns.')
                    return redirect('leads_list')

                created = 0
                for _, row in df.iterrows():
                    if pd.isna(row.get('email')):
                        continue

                    Lead.objects.create(
                        first_name=row.get('name', 'Unknown'),
                        email=row.get('email'),
                        organization_name='Imported',
                        lead_owner=request.user
                    )
                    created += 1

                messages.success(request, f'{created} leads uploaded successfully.')

            except Exception as e:
                messages.error(request, f'Upload failed: {str(e)}')

            return redirect('leads_list')
    else:
        form = LeadUploadForm()

    return render(request, 'lead/upload_leads.html', {
        'form': form
    })


@login_required
def pipeline(request):
    leads = Lead.objects.filter(
        lead_owner=request.user,
        deleted_at__isnull=True
    )

    pipeline = {
        'new': leads.filter(status='new'),
        'contacted': leads.filter(status='contacted'),
        'qualified': leads.filter(status='qualified'),
        'won': leads.filter(status='won'),
        'lost': leads.filter(status='lost'),
    }

    return render(request, 'lead/leads_pipeline.html', {
        'pipeline': pipeline
    })


@login_required
def update_lead_status(request, pk):
    lead = get_object_or_404(
        Lead,
        pk=pk,
        lead_owner=request.user
    )

    if request.method == 'POST':
        data = json.loads(request.body)
        status = data.get('status')

        if status in dict(Lead.STATUS_CHOICES):
            lead.status = status
            lead.save()

    return HttpResponse(status=204)
