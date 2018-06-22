from django.shortcuts import redirect, render
from django.contrib.auth import views
from django.contrib.auth.views import LoginView, TemplateView


def redirect_to_login(request):
    return redirect('accounts:login', permanent=True)


class TMLogin(LoginView):
    redirect_authenticated_user = True


class TMRegister(TemplateView):


    def get(self, request, *args):
        pass

    def post(self, request):
        pass
