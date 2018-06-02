from django.shortcuts import get_object_or_404, get_list_or_404, render
from .models import Request


def index(request):
    return render(request, "purchaseRequests/index.html")

def list(request):
    #TODO: don't throw a 404 here, need to fail by showing that there are no requests
    pur_req_list = get_list_or_404(Request)
    return render(request, "purchaseRequests/list.html", {'pur_req_list': pur_req_list})

def new(request):
    return render(request, "purchaseRequests/new_request.html")

def detail(request, pReq_id):
    pur_req = get_object_or_404(Request, pk=pReq_id)
    return render(request, "purchaseRequests/detail.html")

def edit(request, pReq_id):
    pur_req = get_object_or_404(Request, pk=pReq_id)
    return render(request, "purchaseRequests/edit.html")

