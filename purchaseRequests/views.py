from purchaseRequests import email_config
from os import environ
import smtplib
from email.message import EmailMessage
from email.utils import make_msgid
from django.shortcuts import get_object_or_404, render
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

def add_request(request):
    new_pur_req = Request.objects.create(timestamp=timezone.now(),
                                         author=request.user,
                                         item=request.POST["item"],
                                         cost=float(request.POST["cost"]),
                                         quantity=int(request.POST["quantity"]),
                                         link=request.POST["link"],)
    message = EmailMessage()

    simple_content = email_config.template_simple_email % (email_config.send_to_person,
                                                           new_pur_req.author.get_username(),
                                                           new_pur_req.item,
                                                           new_pur_req.timestamp.strftime('%m/%d/%Y'),
                                                           new_pur_req.item,
                                                           new_pur_req.cost,
                                                           new_pur_req.quantity,
                                                           new_pur_req.cost * new_pur_req.quantity,
                                                           new_pur_req.link,)
    html_content = email_config.template_simple_email % (email_config.send_to_person,
                                                         new_pur_req.author.get_username(),
                                                         new_pur_req.item,
                                                         new_pur_req.timestamp.strftime('%m/%d/%Y'),
                                                         new_pur_req.item,
                                                         new_pur_req.cost,
                                                         new_pur_req.quantity,
                                                         new_pur_req.cost * new_pur_req.quantity,
                                                         new_pur_req.link,)
    html_content.format(asparagus_cid=make_msgid()[1:-1])

    message.set_content(simple_content)
    message.add_alternative(html_content, subtype='html')
    message["Subject"] = "New Purchase Request for %s" % new_pur_req.item
    message["From"] = email_config.app_email
    message["To"] = email_config.send_to_email

    server = smtplib.SMTP(email_config.app_smtp_server, 587)
    server.starttls()
    server.login(email_config.app_email, environ.get("APP_PASS"))
    server.send_message(message, email_config.app_email, email_config.send_to_email)
    server.quit()

    return HttpResponseRedirect(reverse("purchaseRequests:detail", args=(new_pur_req.id,)))
