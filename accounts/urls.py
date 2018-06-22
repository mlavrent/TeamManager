from django.urls import path, include
from . import views

app_name = "accounts"
urlpatterns = [
    path("", views.redirect_to_login),
    path("login/", views.TMLogin.as_view(), name="login"),
    path("join/", views.TMRegister.as_view(), name="signup"),
    path("", include("django.contrib.auth.urls")),
]