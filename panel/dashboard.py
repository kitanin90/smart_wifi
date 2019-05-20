from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.utils import timezone

from django.db.models import Sum, F
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from panel.const import BYTES_IN_MB
from panel.models import Client, NAS, Session


@require_http_methods(["GET"])
@login_required
def index(request):
    now = timezone.now()

    template_data = {"month_traffic": get_traffic_from_date(now - timedelta(days=30)),
                     "week_traffic": get_traffic_from_date(now - timedelta(days=7)),
                     "day_traffic": get_traffic_from_date(now - timedelta(days=1)),
                     "top_clients": get_top10_clients_from_date(now - timedelta(days=30)),
                     "top_points": get_top10_points_from_date(now - timedelta(days=30))
                     }

    return render(request, 'panel/dashboard.html', template_data)


def get_traffic_from_date(date):
    return Session.objects.filter(acctstarttime__gte=date).aggregate(
        download=Sum("acctinputoctets") / BYTES_IN_MB,
        upload=Sum("acctoutputoctets") / BYTES_IN_MB
    )


def get_top10_clients_from_date(date):
    # TODO: FIX None
    top_clients = Session.objects.filter(acctstarttime__gte=date).values('username').annotate(
        traffic=Sum((F("acctinputoctets") + F("acctoutputoctets")) / BYTES_IN_MB)
    ).order_by('-traffic')[:10]

    for client in top_clients:
        client["obj"] = Client.objects.get(username=client["username"])

    return top_clients


def get_top10_points_from_date(date):
    # TODO: FIX None
    top_points = Session.objects.filter(acctstarttime__gte=date).values('calledstationid').annotate(
        traffic=Sum((F("acctinputoctets") + F("acctoutputoctets")) / BYTES_IN_MB)
    ).order_by('-traffic')[:10]

    for point in top_points:
        point["obj"] = NAS.objects.get(mac=point["calledstationid"])

    return top_points
