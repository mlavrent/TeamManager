from purchaseRequests import email_config
from team_manager import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchVector
from .models import Request
import csv
from datetime import datetime, timedelta
import pytz

class HttpResponseSeeOther(HttpResponseRedirect):
    status_code = 303


@login_required
def list(request):
    pur_reqs = Request.objects.all()

    in_format = "%m/%d/%Y"
    db_format = "%Y-%m-%d"

    # Date filters
    if "start" in request.GET and request.GET["start"]:
        st = datetime.strptime(request.GET["start"], in_format)
        st = st.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime(db_format)
        print(st)
        pur_reqs = pur_reqs.filter(timestamp__gte=st)

    if "end" in request.GET and request.GET["end"]:
        et = datetime.strptime(request.GET["end"], in_format)
        et += timedelta(days=1)
        et = et.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime(db_format)
        print(et)
        pur_reqs = pur_reqs.filter(timestamp__lt=et)

    # Search bar
    # if "q" in request.GET and request.GET["q"].startswith("user:"):
    #     user_search = request.GET["q"][5:]
    #     #pur_reqs = pur_reqs.annotate(search=SearchVector()).filter(search=user_search)
    # elif "q" in request.GET and request.GET["q"]:
    #     pur_reqs = pur_reqs.annotate(
    #         search=SearchVector("item"),
    #     ).filter(search=request.GET["q"])

    context = {
        'pur_req_list': pur_reqs.order_by('-timestamp'),
        'theme_color': settings.THEME_COLOR,
    }
    return render(request, "purchaseRequests/list.html", context)


@login_required
def export(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="purchase_requests.csv"'

    writer = csv.writer(response)
    writer.writerow(['id', 'date', 'time', 'author', 'price per unit', 'quantity', 'total cost', 'link', 'approved?'])

    for pur_req in Request.objects.all().order_by('-timestamp').values():
        timestamp = pur_req['timestamp'].astimezone(pytz.timezone(settings.TIME_ZONE))
        writer.writerow([
            pur_req['id'],
            timestamp.strftime("%b %d, %Y"),
            timestamp.strftime("%H:%M"),
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
                                             link=request.POST["link"],)

        path_to_req = request.build_absolute_uri(reverse("purchaseRequests:detail", args=(new_pur_req.id,)))

        simple_content = email_config.template_simple_email % (email_config.send_to_person,
                                                               new_pur_req.author.get_username(),
                                                               new_pur_req.item,
                                                               new_pur_req.timestamp.strftime('%m/%d/%Y'),
                                                               new_pur_req.item,
                                                               new_pur_req.cost,
                                                               new_pur_req.quantity,
                                                               new_pur_req.cost * new_pur_req.quantity,
                                                               new_pur_req.link,
                                                               path_to_req)
        html_content = email_config.template_html_email % (email_config.send_to_person,
                                                           new_pur_req.author.get_username(),
                                                           new_pur_req.item,
                                                           new_pur_req.timestamp.strftime('%m/%d/%Y'),
                                                           new_pur_req.item,
                                                           new_pur_req.cost,
                                                           new_pur_req.quantity,
                                                           new_pur_req.cost * new_pur_req.quantity,
                                                           new_pur_req.link,
                                                           new_pur_req.link,
                                                           path_to_req)

        send_mail(subject="New purchase request for %s" % new_pur_req.item,
                  message=simple_content,
                  from_email=settings.EMAIL_HOST_USER,
                  recipient_list=email_config.send_to_emails,
                  html_message=html_content)

        return HttpResponseRedirect(path_to_req)
    else:
        return render(request, "purchaseRequests/new_request.html", {'theme_color': settings.THEME_COLOR})
