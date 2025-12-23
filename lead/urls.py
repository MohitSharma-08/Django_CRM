from django.urls import path

from . import views

urlpatterns = [
    path('', views.leads_list, name='leads_list'),
    path('add-lead/', views.add_lead, name='add_lead'),
    path('<int:pk>/', views.leads_detail, name='leads_detail'),
    path('<int:pk>/delete/', views.leads_delete, name='leads_delete'),
    path('<int:pk>/edit/', views.leads_edit, name='leads_edit'),
    path('<int:pk>/convert/', views.convert_to_client, name='leads_convert'),
    path('upload/', views.upload_leads, name='upload_leads'),
    path('pipeline/', views.pipeline, name='leads_pipeline'),
    path('pipeline/<int:pk>/update/', views.update_lead_status, name='update_lead_status'),

]