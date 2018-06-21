from django.shortcuts import redirect, render
from django.contrib.auth import views


def redirect_to_login(request):
    return redirect('accounts:login', permanent=True)


def login(request, **kwargs):
    if request.user.is_authenticated:
        return redirect('purchaseRequests:list')
    else:
        return views.login(request, **kwargs)


def signup(request):
    return render(request, "registration/signup.html")
