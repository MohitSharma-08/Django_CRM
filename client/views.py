from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from .models import Client
from .forms import AddClientForm

@login_required
def clients_list(request):
    clients = Client.objects.filter(
        created_by = request.user,
        deleted_at__isnull = True,

        )
    
    paginator = Paginator(clients, 10)
    page_number = request.GET.get('page')
    clients_page = paginator.get_page(page_number)

    return render(request, 'client/clients_list.html' ,{
        'clients': clients_page
    }) 

@login_required
def clients_detail(request, pk):
    client = get_object_or_404(
        Client,
        pk=pk,
        created_by = request.user,
    )

    return render(request, 'client/clients_detail.html', {
        'client': client
    })

# delete clients
@login_required
def clients_delete(request, pk):
    client = get_object_or_404(Client, pk=pk, created_by = request.user)
    

    if request.method == 'POST':
        client.deleted_at = timezone.now()
        client.deleted_by = request.user
        client.save()

    messages.success(request, 'Client deleted successfully')

    return redirect('clients_list')


# edit client
def clients_edit(request, pk):
    client = get_object_or_404(Client, pk=pk, created_by = request.user)

    if request.method == 'POST':
        form = AddClientForm(request.POST, instance=client)

        if form.is_valid():
            form.save()

            messages.success(request, "Changes applied.")

            return redirect('clients_list')

    else:
        form = AddClientForm(instance=client)

    return render(request, 'client/clients_edit.html', {
        'form': form
    })

# add Client
@login_required
def clients_add(request):

    if request.method == 'POST':
        form = AddClientForm(request.POST)

        if form.is_valid():
            client = form.save(commit=False)
            client.created_by = request.user
            client.save()

            messages.success(request, 'The Client was Created.')


            return redirect('clients_list')
        
        else:
            for error in form.errors.values():
                messages.error(request, error.as_text().replace('* ', ''))


    else:
        form = AddClientForm()

    return render(request, 'client/clients_add.html',{
    'form': form
    })