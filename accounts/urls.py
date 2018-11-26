from django.urls import path, include
from . import views

app_name = "accounts"
urlpatterns = [
    path("", views.redirect_to_login),
    path("login/", views.LoginView.as_view(), name="login"),
    path("join/", views.signup, name="signup"),
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),
    path("", include("django.contrib.auth.urls")),
]