from django.urls import path
from . import views

urlpatterns = [
    path("", views.list, name="index"),
    path("list/", views.list, name="list"),
    path("new/", views.new, name="new"),
    path("<int:pReq_id>", views.detail, name="detail"),
    path("<int:pReq_id>/edit", views.edit, name="edit"),
]

