from datetime import datetime, timedelta

from django.db.models import Count, Sum
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from panel.models import Faculty, Client, Building, NAS, Session


@require_http_methods(["GET"])
def index(request):
    month_traffic = get_traffic_from_date(datetime.now() - timedelta(days=30))
    week_traffic = get_traffic_from_date(datetime.now() - timedelta(days=7))
    day_traffic = get_traffic_from_date(datetime.now() - timedelta(days=1))

    return render(request, 'panel/dashboard.html',
                  {"month_traffic": month_traffic, "week_traffic": week_traffic, "day_traffic": day_traffic})


def get_traffic_from_date(date):
    traffic = Session.objects.filter(acctstarttime__gte=date).aggregate(
        download=Sum("acctinputoctets"),
        upload=Sum("acctoutputoctets")
    )

    return {"download": round(traffic["download"] / 1024 / 1024),
            "upload": round(traffic["upload"] / 1024 / 1024)}
