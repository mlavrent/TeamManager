from purchaseRequests import email_config
from team_manager import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Request
import csv


class HttpResponseSeeOther(HttpResponseRedirect):
    status_code = 303


@login_required
def list(request):
    pur_req_list = Request.objects.all().order_by('-timestamp')

    context = {
        'pur_req_list': pur_req_list,
        'theme_color': settings.THEME_COLOR,
    }
    return render(request, "purchaseRequests/list.html", context)


@login_required
def export(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="purchase_requests.csv"'

    writer = csv.writer(response)
    writer.writerow(['id', 'timestamp', 'author', 'price per unit', 'quantity', 'total cost', 'link', 'approved?'])

    for pur_req in Request.objects.all().order_by('-timestamp').values():
        writer.writerow([
            pur_req['id'],
            pur_req['timestamp'],
            User.objects.get(pk=pur_req['author_id']).get_username(),
            pur_req['cost'],
            pur_req['quantity'],
            pur_req['cost'] * pur_req['quantity'],
            pur_req['link'],
            pur_req['approved'],
        ])

    return response

@login_required
def detail(request, pReq_id):
    pur_req = get_object_or_404(Request, pk=pReq_id)

    if request.method == "POST":
        if "den-but" in request.POST:
            pur_req.approved = False
        elif "app-but" in request.POST:
            pur_req.approved = True
        elif "und-but" in request.POST:
            pur_req.approved = None
        pur_req.save()
        return HttpResponseSeeOther(reverse("purchaseRequests:change_preq_status", kwargs={"pReq_id": pReq_id}))

    authorized = request.user.groups.filter(name="Approvers").exists() or request.user.is_superuser
    selectable = "sel" if authorized else ""
    disable_buttons = "" if authorized else "disabled"
    state = ["", "", ""]
    if pur_req.approved is True:
        state[2] = "current-state"
    elif pur_req.approved is False:
        state[0] = "current-state"
    else:
        state[1] = "current-state"

    return render(request, "purchaseRequests/detail.html", {"pur_req": pur_req,
                                                            "state": state,
                                                            "selectable": selectable,
                                                            "disable_buttons": disable_buttons,})


def change_preq_status(request, pReq_id):
    return redirect("purchaseRequests:detail", pReq_id)



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
            context = {
                'pur_req': pur_req,
                'theme_color': settings.THEME_COLOR,
                'lt_theme_color': settings.LIGHT_THEME_COLOR,
            }
            return render(request, "purchaseRequests/edit.html", context)
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
                  from_email=settings.EMAIL_HOST_USER,
                  recipient_list=email_config.send_to_emails,
                  html_message=html_content)

        return HttpResponseRedirect(reverse("purchaseRequests:detail", args=(new_pur_req.id,)))
    else:
        return render(request, "purchaseRequests/new_request.html", {'theme_color': settings.THEME_COLOR})
