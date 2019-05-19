from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from datetime import timedelta
from django.utils import timezone
from panel.models import Faculty, Client, Building, NAS


@require_http_methods(["GET"])
def connect(request):
    return render(request, 'captive/index.html')


@require_http_methods(["GET"])
def successful_connect(request):
    return render(request, 'captive/successful.html')


@require_http_methods(["GET", "POST"])
@csrf_protect
def auth(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
    else:
        return render(request, 'panel/auth.html')


@require_http_methods(["GET"])
@login_required
def logout_view(request):
    logout(request)
    return redirect('auth')


@require_http_methods(["GET"])
@login_required
def points(request):
    building_list = Building.objects.all()
    nas_list = None

    if "building_id" in request.GET:
        building_id = request.GET["building_id"]
        building = Building.objects.get(id=building_id)
        nas_list = NAS.objects.filter(building=building)

    return render(request, 'panel/points.html', {"building_list": building_list, "nas_list": nas_list})


@require_http_methods(["GET"])
@login_required
def point(request, nas_id):
    nas = NAS.objects.get(id=nas_id)

    now = timezone.now()

    month_traffic = nas.get_traffic_from_date(now - timedelta(days=30))
    week_traffic = nas.get_traffic_from_date(now - timedelta(days=7))
    day_traffic = nas.get_traffic_from_date(now - timedelta(days=1))

    return render(request, 'panel/point.html',
                  {"nas": nas, "month_traffic": month_traffic, "week_traffic": week_traffic,
                   "day_traffic": day_traffic})


@require_http_methods(["GET"])
@login_required
def clients(request):
    faculty_list = Faculty.objects.all()
    client_list = None
    faculty = None

    if "faculty_id" in request.GET:
        faculty_id = request.GET["faculty_id"]
        faculty = Faculty.objects.get(id=faculty_id)
        client_list = Client.objects.filter(faculty=faculty)

    return render(request, 'panel/clients.html',
                  {"faculty_list": faculty_list, "client_list": client_list, "faculty": faculty})


@require_http_methods(["GET"])
@login_required
def client(request, client_id):
    client = Client.objects.get(id=client_id)

    now = timezone.now()

    month_traffic = client.get_traffic_from_date(now - timedelta(days=30))
    week_traffic = client.get_traffic_from_date(now - timedelta(days=7))
    day_traffic = client.get_traffic_from_date(now - timedelta(days=1))

    month_time = client.get_time_from_date(now - timedelta(days=30))
    week_time = client.get_time_from_date(now - timedelta(days=7))
    day_time = client.get_time_from_date(now - timedelta(days=1))

    return render(request, 'panel/client.html',
                  {"client": client, "month_traffic": month_traffic, "week_traffic": week_traffic,
                   "day_traffic": day_traffic, "month_time": month_time, "week_time": week_time, "day_time": day_time})
