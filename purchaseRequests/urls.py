from django.urls import path
from . import views

app_name = "purchaseRequests"
urlpatterns = [
    path("", views.list, name="list"),
    path("new/", views.new_request, name="new"),
    path("<int:pReq_id>", views.detail, name="detail"),
    path("<int:pReq_id>/edit", views.edit, name="edit"),
    path("add-request/", views.add_request, name="add_request"),
    path("delete-request/", views.delete_request, name="delete_request"),
    path("<int:pReq_id>/edit-request", views.edit_request, name="edit_request"),
]

