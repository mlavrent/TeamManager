from django.shortcuts import redirect, render
from django.contrib.auth import views


def redirect_to_login(request):
    return redirect('login', permanent=True)


def login(request, **kwargs):
    if request.user.is_authenticated:
        return redirect('/purchase-requests', app_name='purchaseRequests')
    else:
        return views.login(request, **kwargs)


def signup(request):
    return render(request, "registration/signup.html")