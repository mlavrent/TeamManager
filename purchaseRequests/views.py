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
from django.db.models import Q, F, Sum, DecimalField
from .models import Request
import csv
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pytz


class HttpResponseSeeOther(HttpResponseRedirect):
    status_code = 303


def validate_date_input(date_str, in_format="%m/%d/%Y"):
    try:
        datetime.strptime(date_str, in_format)
        return True
    except ValueError:
        return False


def gen_dt_bin_data(raw_data, bin_start, bin_end):
    bin_reqs = raw_data.filter(timestamp__gte=bin_start, timestamp__lt=bin_end)
    bin_apps = raw_data.filter(approved_timestamp__gte=bin_start, approved_timestamp__lt=bin_end)
    bin_ords = raw_data.filter(order_timestamp__gte=bin_start, order_timestamp__lt=bin_end)
    bin_dels = raw_data.filter(delivery_timestamp__gte=bin_start, delivery_timestamp__lt=bin_end)

    return {'t': bin_start.strftime("%Y-%m-%d %H:%M"),
            'y': bin_reqs.count() + bin_apps.count() + bin_ords.count() + bin_dels.count()},\
           {'t': bin_start.strftime("%Y-%m-%d %H:%M"),
            'y': float(bin_ords.aggregate(t=Sum(F('cost') * F('quantity'), output_field=DecimalField()))["t"] or 0.00) +
                 float(bin_ords.exclude(shipping_cost__isnull=True).aggregate(sc=Sum('shipping_cost'))["sc"] or 0.00)}


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
    in_format = "%b %d, %Y"
    db_format = "%Y-%m-%d"

    earliest_req_time = pur_reqs.earliest('timestamp').timestamp
    # Date filtering
    if "dr" in request.GET and " - " in request.GET["dr"]:
        st, et = request.GET["dr"].split(" - ")
        if validate_date_input(st, in_format) and validate_date_input(et, in_format):
            st = datetime.strptime(st, in_format)
            et = datetime.strptime(et, in_format) + timedelta(days=1)

            start_time = st
            end_time = et

            st = st.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime(db_format)
            et = et.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime(db_format)

            pur_reqs = pur_reqs.filter((Q(timestamp__gte=st) | Q(approved_timestamp__gte=st) |
                                        Q(order_timestamp__gte=st) | Q(delivery_timestamp__gte=st)) &
                                       (Q(timestamp__lte=et) | Q(approved_timestamp__lte=et) |
                                        Q(order_timestamp__lte=et) | Q(delivery_timestamp__lte=et)))
        else:
            start_time = earliest_req_time
            end_time = timezone.now()
    else:
        start_time = earliest_req_time
        end_time = timezone.now()


    # Data generation for the chart
    activity = []
    spending = []

    range_width = end_time - start_time
    print(range_width)
    if range_width <= timedelta(days=1):
        interval = "hour"
        start_time = datetime(start_time.year, start_time.month, start_time.day, hour=start_time.hour, minute=0,
                              second=0, microsecond=0, tzinfo=start_time.tzinfo)
        round_up = 0 if end_time.minute == 0 and end_time.second == 0 and end_time.microsecond == 0 else 1
        end_time = datetime(end_time.year, end_time.month, end_time.day, hour=end_time.hour + round_up, minute=0,
                            second=0, microsecond=0, tzinfo=end_time.tzinfo)

        range_width = end_time - start_time
        num_bins = int((range_width.days * 86400 + range_width.seconds) / 3600)
    elif range_width <= timedelta(days=6):
        interval = "several-hour"
        num_days = range_width.days

        start_time = datetime(start_time.year, start_time.month, start_time.day,
                              hour=int(start_time.hour/num_days)*num_days, minute=0, second=0, microsecond=0,
                              tzinfo=start_time.tzinfo)
        round_up = 0 if end_time.minute == 0 and end_time.second == 0 and end_time.microsecond == 0 else num_days
        end_time = datetime(end_time.year, end_time.month, end_time.day,
                            hour=int(end_time.hour/num_days)*num_days + round_up, minute=0, second=0, microsecond=0,
                            tzinfo=end_time.tzinfo)

        range_width = end_time - start_time
        num_bins = int((range_width.days * 86400 + range_width.seconds) / (3600 * num_days))
    elif range_width <= timedelta(weeks=3):
        interval = "day"
        start_time = datetime(start_time.year, start_time.month, start_time.day, tzinfo=start_time.tzinfo)
        round_up = 0 if end_time.minute == 0 and end_time.second == 0 and end_time.microsecond == 0 else 2
        end_time = datetime(end_time.year, end_time.month, end_time.day, tzinfo=end_time.tzinfo)

        range_width = end_time - start_time
        num_bins = range_width.days
    elif end_time <= start_time + relativedelta(months=+6):
        interval = "week"
        start_time = datetime(start_time.year, start_time.month, start_time.day)
        start_time = start_time - timedelta(days=start_time.isoweekday() % 7)

        end_time = datetime(end_time.year, end_time.month, end_time.day)
        end_time = end_time + timedelta(days=7 - (end_time.isoweekday() % 7))

        range_width = end_time - start_time
        num_bins = int(range_width.days / 7)
    elif end_time <= start_time + relativedelta(years=+2):
        interval = "month"
        # For up to two years, do by month
        for n in range(12 * (end_time.year - start_time.year) + end_time.month - start_time.month + 1):
            bin_start = datetime(start_time.year, start_time.month, 1) + (n * relativedelta(months=+1))
            bin_end = bin_start + relativedelta(months=+1)

            m_activity, m_spending = gen_dt_bin_data(pur_reqs, bin_start, bin_end)
            activity.append(m_activity)
            spending.append(m_spending)
        num_bins = 0
    else:
        interval = "year"
        for n in range(end_time.year - start_time.year + 1):
            bin_start = datetime(start_time.year, 1, 1) + relativedelta(years=+n)
            bin_end = bin_start + relativedelta(years=+1)

            m_activity, m_spending = gen_dt_bin_data(pur_reqs, bin_start, bin_end)
            activity.append(m_activity)
            spending.append(m_spending)
        num_bins = 0

    if num_bins:
        bin_width = (end_time - start_time) / num_bins
        for n in range(num_bins):
            bin_start = start_time + (n * bin_width)
            bin_end = bin_start + bin_width

            bin_activity, bin_spending = gen_dt_bin_data(pur_reqs, bin_start, bin_end)
            activity.append(bin_activity)
            spending.append(bin_spending)

    # Bottom summary data
    app_reqs = pur_reqs.filter(approved=True)
    team_data = {
        'num_reqs': pur_reqs.count(),
        'num_app': app_reqs.count(),
        'total_req': pur_reqs.aggregate(total=Sum(F('quantity') * F('cost'), output_field=DecimalField()))["total"],
        'total_app': app_reqs.aggregate(total=Sum(F('quantity') * F('cost'), output_field=DecimalField()))["total"],
    }
    if team_data['total_req'] is None:
        team_data['total_req'] = 0
    if team_data['total_app'] is None:
        team_data['total_app'] = 0

    user_reqs = pur_reqs.filter(author=request.user)
    user_app_reqs = user_reqs.filter(approved=True)
    user_data = {
        'num_reqs': user_reqs.count(),
        'num_app': user_app_reqs.count(),
        'total_req': user_reqs.aggregate(total=Sum(F('quantity') * F('cost'), output_field=DecimalField()))["total"],
        'total_app': user_app_reqs.aggregate(total=Sum(F('quantity') * F('cost'), output_field=DecimalField()))["total"],
    }
    if user_data['total_req'] is None:
        user_data['total_req'] = 0
    if user_data['total_app'] is None:
        user_data['total_app'] = 0

    context = {
        'activity': activity,
        'spending': spending,
        'team_data': team_data,
        'user_data': user_data,
        'earliest_req': earliest_req_time.strftime(db_format),
        'start_date': start_time.strftime(db_format),
        'end_date': end_time.strftime(db_format),
        'interval': interval,
        'theme_color': settings.THEME_COLOR,
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
