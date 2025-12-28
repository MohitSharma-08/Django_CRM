from django.urls import path
from django.shortcuts import redirect
from . import views

urlpatterns = [
    path('add-lead/<int:step>/', views.lead_wizard, name='add_lead_step'),
    path('<int:pk>/edit/<int:step>/', views.lead_wizard, name='edit_lead_step'),
    # List & detail
    path('', views.leads_list, name='leads_list'),
    path('<int:pk>/', views.leads_detail, name='leads_detail'),
    # Edit / Delete
    path('<int:pk>/delete/', views.leads_delete, name='leads_delete'),
    # Convert
    path('<int:pk>/convert/', views.convert_to_client, name='leads_convert'),

    # Upload
    path('upload/', views.upload_leads, name='upload_leads'),

    # Pipeline
    path('pipeline/', views.pipeline, name='leads_pipeline'),
    path('pipeline/<int:pk>/update/', views.update_lead_status, name='update_lead_status'),
]
