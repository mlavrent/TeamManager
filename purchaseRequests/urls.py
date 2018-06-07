from django.urls import path
from . import views

app_name = "purchaseRequests"
urlpatterns = [
    path("", views.list, name="list"),
    path("new/", views.new_request, name="new"),
    path("<int:pReq_id>", views.detail, name="detail"),
    path("<int:pReq_id>/edit", views.edit, name="edit"),
]

