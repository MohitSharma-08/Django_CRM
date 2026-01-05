from django.urls import reverse

def redirect_by_role(user):
    role = user.role.role

    if role in ['superadmin', 'admin', 'employee']:
        return reverse('dashboard')
    elif role == 'client':
        return reverse('index')

    return reverse('index')
