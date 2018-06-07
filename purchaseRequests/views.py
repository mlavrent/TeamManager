from django.shortcuts import get_object_or_404, get_list_or_404, render
from django.contrib.auth.decorators import login_required
from .models import Request

@login_required
def list(request):
    pur_req_list = Request.objects.all().order_by('-timestamp')
    return render(request, "purchaseRequests/list.html", {'pur_req_list': pur_req_list})

@login_required
def detail(request, pReq_id):
    pur_req = get_object_or_404(Request, pk=pReq_id)
    unappr = ""
    undec = ""
    appr = ""
    if pur_req.approved is True:
        appr = "selected-appr"
    elif pur_req.approved is False:
        unappr = "selected-unappr"
    else:
        undec = "selected-undec"

    return render(request, "purchaseRequests/detail.html", {'pur_req': pur_req,
                                                            'unappr_class': unappr,
                                                            'undec_class': undec,
                                                            'appr_class': appr,})

@login_required
def edit(request, pReq_id):
    pur_req = get_object_or_404(Request, pk=pReq_id)
    return render(request, "purchaseRequests/edit.html")

@login_required
def new_request(request):
    return render(request, "purchaseRequests/new_request.html")
