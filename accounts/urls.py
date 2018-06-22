from django.urls import path, include
from . import views

app_name = "accounts"
urlpatterns = [
    path("", views.redirect_to_login),
    path("login/", views.login, name="login"),
    path("join/", views.signup, name="signup"),
    path("", include("django.contrib.auth.urls")),
]