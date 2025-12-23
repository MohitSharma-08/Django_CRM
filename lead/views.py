import pandas as pd

import json

from django.http import HttpResponse
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import Lead
from .forms import AddLeadForm, LeadUploadForm

from client.models import Client

@login_required
def leads_list(request):
    leads = Lead.objects.filter(
        created_by = request.user,
        deleted_at__isnull = True,
        converted_to_client = False                    
        )  
    
    paginator = Paginator(leads, 10)

    page_number = request.GET.get('page')

    leads_page = paginator.get_page(page_number)

    # leads = Lead.objects.all()
    # make all leads visible

    return render(request, 'lead/leads_list.html', {
        'leads': leads_page
    })

# lead details
@login_required
def leads_detail(request, pk):
    lead = get_object_or_404(
        Lead, pk=pk, created_by = request.user, deleted_at__isnull = True
    )

    return render(request, 'lead/leads_details.html', {
        'lead': lead
    })

# delete leads
@login_required
def leads_delete(request, pk):
    lead = get_object_or_404(Lead, pk=pk, created_by = request.user)
    
    # lead.delete()

    if request.method == 'POST':
        lead.deleted_at = timezone.now()
        lead.deleted_by = request.user
        lead.save()

    messages.success(request, 'Lead deleted successfully')

    return redirect('leads_list')

# edit leads
@login_required
def leads_edit(request, pk):
    lead = get_object_or_404(Lead, created_by = request.user, pk=pk)

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
    

# add leads
@login_required
def add_lead(request):

    if request.method == 'POST':
        form = AddLeadForm(request.POST)

        if form.is_valid():
            lead = form.save(commit=False)
            lead.created_by = request.user
            lead.save()

            messages.success(request, 'The lead was Created.')


            return redirect('leads_list')
    else:
        form = AddLeadForm()

    return render(request, 'lead/add_lead.html',{
    'form': form
    })


@login_required
def convert_to_client(request, pk):
    lead = get_object_or_404(Lead, created_by = request.user, pk=pk)

    client = Client.objects.create(
        name = lead.name,
        email = lead.email,
        description = lead.description,
        created_by = request.user,
    )

    lead.converted_to_client = True
    lead.save()

    messages.success(request, 'The lead was successfully converted to a client.')

    return redirect('leads_list')


# uploading leads through files
@login_required
def upload_leads(request):
    if request.method == 'POST':
        form = LeadUploadForm(request.POST, request.FILES)

        if form.is_valid():
            file = request.FILES['file']

            try:
                # Read file
                if file.name.endswith('.csv'):
                    df = pd.read_csv(file)
                elif file.name.endswith('.xlsx'):
                    df = pd.read_excel(file)
                else:
                    messages.error(request, 'Unsupported file format.')
                    return redirect('leads_list')

                required_columns = {'name', 'email', 'description', 'priority', 'status'}

                if not required_columns.issubset(df.columns.str.lower()):
                    messages.error(request, 'Excel file has missing columns.')
                    return redirect('leads_list')

                created = 0

                for _, row in df.iterrows():
                    if pd.isna(row['email']):
                        continue  # skip bad rows

                    Lead.objects.create(
                        name=row['name'],
                        email=row['email'],
                        description=row.get('description', ''),
                        priority=row.get('priority', 'medium'),
                        status=row.get('status', 'new'),
                        created_by=request.user
                    )
                    created += 1

                messages.success(request, f'{created} leads uploaded successfully.')

            except Exception as e:
                messages.error(request, f'Upload failed: {str(e)}')

            return redirect('leads_list')

    else:
        form = LeadUploadForm()

    return render(request, 'lead/upload_leads.html', {'form': form})


# pipeline functionality
@login_required
def pipeline(request):
    lead = Lead.objects.filter(
        created_by = request.user,
        deleted_at__isnull = True
    )

    pipeline = {
        'new': lead.filter(status='new'),
        'contacted': lead.filter(status='contacted'),
        'qualified': lead.filter(status='qualified'),
        'won': lead.filter(status='won'),
        'lost': lead.filter(status='lost'),
    }

    return render(request, 'lead/leads_pipeline.html', {
        'pipeline': pipeline
    })

# status change of leads
@login_required
def update_lead_status(request, pk):
    lead = get_object_or_404(
        Lead,
        pk = pk,
        created_by = request.user
    ) 

    if request.method == 'POST':
        data = json.loads(request.body)
        status = data.get('status')
        
        if status in dict(Lead.CHOICES_STATUS):
            lead.status = status
            lead.save()

    return HttpResponse(status = 204)