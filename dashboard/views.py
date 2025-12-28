from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.cache import never_cache

from client.models import Client
from lead.models import Lead


@login_required
@never_cache
def dashboard(request):
    # Leads owned by the logged-in user
    leads = Lead.objects.filter(
        lead_owner=request.user,        
        deleted_at__isnull=True
    )

    # Clients created by the user (Client model DOES have created_by)
    total_clients = Client.objects.filter(
        created_by=request.user
    ).count()

    pipeline = {
        'new': leads.filter(status='new'),
        'contacted': leads.filter(status='contacted'),
        'qualified': leads.filter(status='qualified'),
        'won': leads.filter(status='won'),
        'lost': leads.filter(status='lost'),
    }

    return render(request, 'dashboard/dashboard.html', {
        'total_clients': total_clients,
        'total_leads': leads.count(),
        'active_leads': leads.exclude(status='lost').count(),
        'pipeline': pipeline,
    })
