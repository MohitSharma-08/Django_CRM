from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Lead
from .forms import AddLeadForm

from client.models import Client

@login_required
def leads_list(request):
    leads = Lead.objects.filter(
        created_by = request.user,
        deleted_at__isnull = True,
        converted_to_client = False                    
        )  

    # leads = Lead.objects.all()
    # make all leads visible

    return render(request, 'lead/leads_list.html', {
        'leads': leads 
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