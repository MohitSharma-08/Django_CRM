from django.contrib import admin
from django.contrib.auth import views
from django.urls import path, include

from accounts.views import index, about
from userprofile.views import signup, CustomLoginView

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', index, name='index'),
    path('dashboard/leads/', include('lead.urls')),
    path('dashboard/clients/', include('client.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('userprofile/', include('userprofile.urls')),
    path('useraccount/', include('useraccount.urls')),
    path('settings/', include('settings.urls')),
    path('about/', about, name='about'),
    path('admin/', admin.site.urls),

    path('sign-up/', signup, name='signup'),
    path('log-in/', CustomLoginView.as_view() ,name='login'),
    path('log-out/', views.LogoutView.as_view(), name='logout'),

]

# Only serve media files through Django during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

