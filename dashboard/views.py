from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.cache import never_cache

from client.models import Client
from lead.models import Lead

# @login_required
# def dashboard(request):
#     total_clients = Client.objects.filter(created_by=request.user).count()
#     total_leads = Lead.objects.filter(created_by=request.user).count()
#     active_leads = Lead.objects.filter(
#         created_by=request.user,
#         status="active"
#     ).count()

#     context = {
#         "total_clients": total_clients,
#         "total_leads": total_leads,
#         "active_leads": active_leads,
#     }

#     return render(request, "dashboard/dashboard.html", context)

@login_required
@never_cache
def dashboard(request):
    leads = Lead.objects.filter(
        created_by=request.user,
        deleted_at__isnull=True
    )

    total_clients = Client.objects.filter(created_by=request.user).count()

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
