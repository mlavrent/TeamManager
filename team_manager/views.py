from django.shortcuts import redirect
from django.contrib.auth import views

def redirect_to_login(request):
    return redirect('login', permanent=True)

def login(request, **kwargs):
    print(request.user.is_authenticated)
    if request.user.is_authenticated:
        return redirect('list', app_name='purchaseRequests')
    else:
        return views.login(request, **kwargs)
