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
from django.db.models import Q
from .models import Request
import csv
from datetime import datetime, timedelta
import pytz

class HttpResponseSeeOther(HttpResponseRedirect):
    status_code = 303

def validate_date_input(date_str, in_format="%m/%d/%Y"):
    try:
        datetime.strptime(date_str, in_format)
        return True
    except ValueError:
        return False


@login_required
def list(request):
    pur_reqs = Request.objects.all()

    in_format = "%m/%d/%Y"
    db_format = "%Y-%m-%d"

    # Date filters
    if "start" in request.GET and validate_date_input(request.GET["start"]):
        st = datetime.strptime(request.GET["start"], in_format)
        st = st.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime(db_format)
        pur_reqs = pur_reqs.filter(timestamp__gte=st)

    if "end" in request.GET and validate_date_input(request.GET["end"]):
        et = datetime.strptime(request.GET["end"], in_format)
        et += timedelta(days=1)
        et = et.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime(db_format)
        pur_reqs = pur_reqs.filter(timestamp__lt=et)

    # Approval filters
    final_query = Q()
    if "den" in request.GET:
        final_query = final_query | Q(approved=False)
    if "und" in request.GET:
        final_query = final_query | Q(approved=None)
    if "app" in request.GET:
        final_query = final_query | Q(approved=True, ordered=False, delivered=False)
    if "ord" in request.GET:
        final_query = final_query | Q(ordered=True, delivered=False)
    if "del" in request.GET:
        final_query = final_query | Q(delivered=True)

    pur_reqs = pur_reqs.filter(final_query)

    # Search bar
    if "q" in request.GET and request.GET["q"]:
        search_terms = request.GET["q"].split()

        product_terms = []
        user_terms = []
        for term in search_terms:
            if term.startswith("user:"):
                user_terms.append(term[5:])
            else:
                product_terms.append(term)

        for p_term in product_terms:
            pur_reqs = pur_reqs.annotate(
                search=SearchVector("item")
            ).filter(search=p_term)

        for u_term in user_terms:
            pur_reqs = pur_reqs.annotate(
                search=SearchVector("author__username")
            ).filter(search=u_term)


    submitted_filters = {
        "start": request.GET["start"] if "start" in request.GET and validate_date_input(request.GET["start"]) else "",
        "end": request.GET["end"] if "end" in request.GET and validate_date_input(request.GET["end"]) else "",
        "q": request.GET["q"] if "q" in request.GET else "",
        "app_checked": "app" in request.GET,
        "und_checked": "und" in request.GET,
        "den_checked": "den" in request.GET,
        "ord_checked": "ord" in request.GET,
        "del_checked": "del" in request.GET,
    }

    context = {
        'pur_req_list': pur_reqs.order_by('-timestamp'),
        'filters': submitted_filters,
        'theme_color': settings.THEME_COLOR,
        'team_name': settings.TEAM_NAME,
    }
    return render(request, "purchaseRequests/list.html", context)


@login_required
def export(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="purchase_requests.csv"'

    writer = csv.writer(response)
    writer.writerow(['id', 'date', 'time', 'author', 'price per unit', 'quantity', 'total cost (w/o shipping)', 'link',
                     'approved?', 'approver', 'approval time',
                     'purchased?', 'purchaser', 'purchase time', 'shipping cost',
                     'delivered?', 'delivery signee', 'delivery time'])

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
            User.objects.get(pk=pur_req['approver_id']).get_username() if pur_req['approver_id'] is not None else "",
            pur_req['approved_timestamp'],
            pur_req['ordered'],
            User.objects.get(pk=pur_req['orderer_id']).get_username() if pur_req['orderer_id'] is not None else "",
            pur_req['order_timestamp'],
            pur_req['shipping_cost'],
            pur_req['delivered'],
            User.objects.get(pk=pur_req['delivery_person_id']).get_username() if pur_req['delivery_person_id']
                                                                                 is not None else "",
            pur_req['delivery_timestamp'],
        ])

    return response


def summary(request):
    pur_reqs = Request.objects.all()
    in_format = "%m/%d/%Y"
    db_format = "%Y-%m-%d"

    if "start" in request.GET and validate_date_input(request.GET["start"]):
        st = datetime.strptime(request.GET["start"], in_format)
        start_time = st.astimezone(pytz.timezone(settings.TIME_ZONE))
        st = st.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime(db_format)
        pur_reqs = pur_reqs.filter(Q(timestamp__gte=st) | Q(approved_timestamp__gte=st) |
                                   Q(order_timestamp__gte=st) | Q(delivery_timestamp__gte=st))
    else:
        start_time = pur_reqs.earliest('timestamp').timestamp

    if "end" in request.GET and validate_date_input(request.GET["start"]):
        et = datetime.strptime(request.GET["end"], in_format)
        et += timedelta(days=1)
        end_time = et.astimezone(pytz.timezone(settings.TIME_ZONE))
        et = et.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime(db_format)
        pur_reqs = pur_reqs.filter(Q(timestamp__lte=et) | Q(approved_timestamp__lte=et) |
                                   Q(order_timestamp__lte=et) | Q(delivery_timestamp__lte=et))
    else:
        end_time = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE))


    # Create 25 bins for the histogram
    num_bins = 15
    bin_width = (end_time - start_time) / num_bins

    added_data = []
    approved_data = []
    order_data = []
    delivery_data = []
    for n in range(num_bins):
        bin_start = start_time + (n * bin_width)
        bin_end = bin_start + bin_width
        bin_mid = bin_start + (bin_width / 2)

        added_data.append(
            {'t': bin_mid.strftime("%Y-%m-%dT%H:%M"),
             'y': pur_reqs.filter(timestamp__gte=bin_start, timestamp__lt=bin_end).count()})
        approved_data.append(
            {'t': bin_mid.strftime("%Y-%m-%dT%H:%M"),
             'y': pur_reqs.filter(approved_timestamp__gte=bin_start, approved_timestamp__lt=bin_end).count()})
        order_data.append(
            {'t': bin_mid.strftime("%Y-%m-%dT%H:%M"),
             'y': pur_reqs.filter(order_timestamp__gte=bin_start, order_timestamp__lt=bin_end).count()})
        delivery_data.append(
            {'t': bin_mid.strftime("%Y-%m-%dT%H:%M"),
             'y': pur_reqs.filter(delivery_timestamp__gte=bin_start, delivery_timestamp__lt=bin_end).count()})


    filters = {
        'start': request.GET["start"] if "start" in request.GET and validate_date_input(request.GET["start"]) else "",
        'end': request.GET["end"] if "end" in request.GET and validate_date_input(request.GET["end"]) else "",
    }
    context = {
        'filters': filters,
        'added_data': added_data,
        'approved_data': approved_data,
        'order_data': order_data,
        'delivery_data': delivery_data,
    }
    return render(request, "purchaseRequests/summary.html", context)


@login_required
def detail(request, pReq_id):
    pur_req = get_object_or_404(Request, pk=pReq_id)
    approval_auth = request.user.groups.filter(name="Approvers").exists()
    purchase_auth = request.user.groups.filter(name="Purchasers").exists()

    if request.method == "POST":
        if "den-but" in request.POST and approval_auth:
            pur_req.approved = False
            pur_req.approver = request.user
            pur_req.approved_timestamp = timezone.now()
        elif "app-but" in request.POST and approval_auth:
            pur_req.approved = True
            pur_req.approver = request.user
            pur_req.approved_timestamp = timezone.now()
        elif "und-but" in request.POST and approval_auth:
            pur_req.approved = None
            pur_req.approver = None
            pur_req.approved_timestamp = None
        elif "shipping" in request.POST and purchase_auth:
            pur_req.shipping_cost = request.POST.get("shipping")
            pur_req.order_timestamp = timezone.now()
            pur_req.orderer = request.user
            pur_req.ordered = True
        elif "delivered" in request.POST and purchase_auth:
            pur_req.delivery_timestamp = timezone.now()
            pur_req.delivery_person = request.user
            pur_req.delivered = True

        pur_req.save()
        return HttpResponseSeeOther(reverse("purchaseRequests:change_preq_status", kwargs={"pReq_id": pReq_id}))
    else:
        selectable = "sel" if approval_auth and not pur_req.ordered else ""
        disable_buttons = "" if approval_auth and not pur_req.ordered else "disabled"
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
                                                                "disable_buttons": disable_buttons,
                                                                "is_purchaser": purchase_auth,})


@login_required
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
        pur_req.notes = request.POST["notes"]

        pur_req.save()
        print(pur_req)
        return redirect("purchaseRequests:detail", pReq_id=pReq_id)
    else:
        pur_req = get_object_or_404(Request, pk=pReq_id)
        if (pur_req.author == request.user or request.user.is_superuser) and pur_req.approved is None:
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
                                             link=request.POST["link"],
                                             notes=request.POST["notes"],)

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
                                                               new_pur_req.notes,
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
                                                           new_pur_req.notes,
                                                           path_to_req)

        approvers = User.objects.filter(groups__name="Approvers").values_list("email", flat=True)
        email_viewers = User.objects.filter(groups__name="Email Viewers").values_list("email", flat=True)
        recipients = approvers | email_viewers

        send_mail(subject="New purchase request for %s" % new_pur_req.item,
                  message=simple_content,
                  from_email=settings.EMAIL_HOST_USER,
                  recipient_list=recipients,
                  html_message=html_content)

        return HttpResponseRedirect(path_to_req)
    else:
        return render(request, "purchaseRequests/new_request.html", {'theme_color': settings.THEME_COLOR})
