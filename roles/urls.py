from django.urls import path
from . import views

app_name = 'roles'

urlpatterns = [
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/update-role/', views.update_user_role, name='update_user_role'),
    path('users/upload/', views.user_upload, name='user_upload'),
    path(    'users/upload/template/',    views.download_user_template,    name='download_user_template'),
    path("permissions/", views.permissions, name="permissions"),

]


