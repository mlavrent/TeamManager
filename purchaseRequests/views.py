from django.shortcuts import render
from django.http import HttpResponse, Http404

def index(request):
    return HttpResponse("This is the purchase request homepage")

def list(request):
    return HttpResponse("This is the list page for all the requests")

def new(request):
    return HttpResponse("This is the page to create a new purchase request")

def detail(request, pReq_id):
    return HttpResponse("This is the detail page for request %s" % pReq_id)

def edit(request, pReq_id):
    return HttpResponse("This is the edit page for %s" % pReq_id)

