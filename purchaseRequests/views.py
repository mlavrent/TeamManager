from purchaseRequests import email_config
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Request


@login_required
def list(request):
    pur_req_list = Request.objects.all().order_by('-timestamp')
    return render(request, "purchaseRequests/list.html", {'pur_req_list': pur_req_list})


@login_required
def detail(request, pReq_id):
    pur_req = get_object_or_404(Request, pk=pReq_id)
    selectable = "sel" if request.user.groups.filter(name="Approver").exists() or request.user.is_superuser else ""

    state = ["", "", ""]
    if pur_req.approved is True:
        state[2] = "current-state"
    elif pur_req.approved is False:
        state[0] = "current-state"
    else:
        state[1] = "current-state"
    print(state, selectable)
    return render(request, "purchaseRequests/detail.html", {"pur_req": pur_req,
                                                            "state": state,
                                                            "selectable": selectable,})


@login_required
def edit(request, pReq_id):
    if request.method == "POST":
        pur_req = get_object_or_404(Request, pk=pReq_id)

        pur_req.item = request.POST["item"]
        pur_req.cost = request.POST["cost"]
        pur_req.quantity = request.POST["quantity"]
        pur_req.link = request.POST["link"]

        pur_req.save()

        return redirect("purchaseRequests:detail", pReq_id=pReq_id)
    else:
        pur_req = get_object_or_404(Request, pk=pReq_id)
        if pur_req.author == request.user or request.user.is_superuser:
            return render(request, "purchaseRequests/edit.html", {'pur_req': pur_req})
        else:
            return redirect('')


def delete_request(request, pReq_id):
    get_object_or_404(Request, pk=pReq_id).delete()
    return redirect("purchaseRequests:list", permanent=True)


@login_required
def new_request(request):
    if request.method == "POST":
        new_pur_req = Request.objects.create(timestamp=timezone.now(),
                                             author=request.user,
                                             item=request.POST["item"],
                                             cost=float(request.POST["cost"]),
                                             quantity=int(request.POST["quantity"]),
                                             link=request.POST["link"], )

        simple_content = email_config.template_simple_email % (email_config.send_to_person,
                                                               new_pur_req.author.get_username(),
                                                               new_pur_req.item,
                                                               new_pur_req.timestamp.strftime('%m/%d/%Y'),
                                                               new_pur_req.item,
                                                               new_pur_req.cost,
                                                               new_pur_req.quantity,
                                                               new_pur_req.cost * new_pur_req.quantity,
                                                               new_pur_req.link,)
        html_content = email_config.template_html_email % (email_config.send_to_person,
                                                           new_pur_req.author.get_username(),
                                                           new_pur_req.item,
                                                           new_pur_req.timestamp.strftime('%m/%d/%Y'),
                                                           new_pur_req.item,
                                                           new_pur_req.cost,
                                                           new_pur_req.quantity,
                                                           new_pur_req.cost * new_pur_req.quantity,
                                                           new_pur_req.link,
                                                           new_pur_req.link,)

        send_mail(subject="New purchase request for %s" % new_pur_req.item,
                  message=simple_content,
                  from_email="lavrema@outlook.com",
                  recipient_list=email_config.send_to_emails,
                  html_message=html_content)

        return HttpResponseRedirect(reverse("purchaseRequests:detail", args=(new_pur_req.id,)))
    else:
        return render(request, "purchaseRequests/new_request.html")
