from random import randint
import csv
import io

import requests
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, render_to_response
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.views.generic import View
from django.shortcuts import get_object_or_404

from datetime import timedelta
from django.utils import timezone
from .forms import FeedbackForm, UploadFileForm

from panel.const import CLEARTEXT_PASSWORD
from panel.models import Faculty, Client, Building, NAS, Session, ClientParameter, GroupReply, UserGroup, Feedback
from smart_wifi.settings import SMSC_LOGIN, SMSC_PASSWORD


@require_http_methods(["GET"])
@ensure_csrf_cookie
def connect(request):
    return render(request, 'captive/index.html')


@require_http_methods(["POST"])
def send_code(request):
    telephone = request.POST["telephone"]

    if not Client.objects.filter(username=telephone).exists():
        client = Client()

        client.sms_auth = True
        client.username = telephone
        client.telephone = telephone

        client.save()

        user_group = UserGroup()

        user_group.groupname = "sms"
        user_group.username = telephone
        user_group.priority = 1

        user_group.save()

    try:
        client_parameter = ClientParameter.objects.filter(username=telephone, attribute=CLEARTEXT_PASSWORD).get()
    except ObjectDoesNotExist:
        client_parameter = ClientParameter()

    client_parameter.username = telephone
    client_parameter.op = ":="
    client_parameter.attribute = CLEARTEXT_PASSWORD

    code = ''.join(["%s" % randint(0, 9) for num in range(0, 6)])

    client_parameter.value = code

    client_parameter.save()

    r = requests.post("https://smsc.ru/sys/send.php",
                      data={'login': SMSC_LOGIN, 'psw': SMSC_PASSWORD, 'phones': "+7" + telephone,
                            "mes": "WiFi code: " + code})

    return HttpResponse("ok")


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


@require_http_methods(["GET"])
@login_required
def session(request, session_id):
    session = Session.objects.get(id=session_id)

    flow_list = session.get_flows()
    paginator = Paginator(flow_list, 50)

    page = request.GET.get('page')
    flows = paginator.get_page(page)

    return render(request, 'panel/session.html', {"session": session, "flows": flows})


@require_http_methods(["GET"])
@login_required
def report(request):
    sessions = None
    start_time = None
    end_time = None

    if "start_time" in request.GET and "end_time" in request.GET:
        start_time = request.GET["start_time"]
        end_time = request.GET["end_time"]

        sessions = Session.objects.filter(acctstarttime__gte=start_time, acctstarttime__lte=end_time).order_by(
            "acctstarttime")

    return render(request, 'panel/report.html', {"sessions": sessions, "start_time": start_time, "end_time": end_time})


@require_http_methods(["GET", "POST"])
@login_required
def settings(request):
    groups = [
        {"name": "students", "title": "Студенты", "params": []},
        {"name": "employees", "title": "Сотрудники", "params": []},
        {"name": "sms", "title": "СМС", "params": []}
    ]
    params = [
        {"name": "Session-Timeout", "title": "Максимальная длительность сессии (секунд)", "multiply": 1},
        {"name": "Idle-Timeout", "title": "Таймаут бездействия (секунд)", "multiply": 1},
        {"name": "WISPr-Bandwidth-Max-Up", "title": "Лимит исходящей скорости (Кб/с)", "multiply": 1000},
        {"name": "WISPr-Bandwidth-Max-Down", "title": "Лимит входящей скорости (Кб/с)", "multiply": 1000}
    ]

    for group in groups:
        for param in params:
            if request.method == "POST":
                input = request.POST["{}-{}".format(group["name"], param["name"])]

                if len(input) > 0:
                    try:
                        reply = GroupReply.objects.get(groupname=group["name"], attribute=param["name"])
                    except ObjectDoesNotExist:
                        reply = GroupReply()

                    reply.groupname = group["name"]
                    reply.attribute = param["name"]
                    reply.op = ":="
                    reply.value = int(input) * param["multiply"]

                    reply.save()
                else:
                    try:
                        reply = GroupReply.objects.get(groupname=group["name"], attribute=param["name"])
                        reply.delete()
                    except ObjectDoesNotExist:
                        pass

            param["value"] = GroupReply.get_value(group["name"], param["name"], param["multiply"])
            group["params"].append(param.copy())

    return render(request, 'panel/settings.html', {"groups": groups})


def feedbacks_list(request):
    feedbacks = Feedback.objects.all()
    return render(request, 'panel/feedback_list.html', context={'feedbacks': feedbacks})


class FeedbackCreate(View):
    def get(self, request):
        form = FeedbackForm()
        return render(request, 'captive/sendfeedback.html', context={'form': form})

    def post(self, request):
        bound_form = FeedbackForm(request.POST)
        if bound_form.is_valid():
            new_post = bound_form.save()
            return redirect('/')
        return render(request, 'captive/sendfeedback.html', context={'form': bound_form})


@require_http_methods(["GET", "POST"])
@csrf_protect
def upload_file(request):
    if request.method == 'POST':
        data = request.FILES["file"].read().decode("cp1251").splitlines()

        reader = csv.reader(data[6:], delimiter=';')

        i = 0
        for row in reader:
            fullname = row[2].replace("  ", " ").strip().split(" ")

            if len(fullname) < 2:
                continue

            password = row[6]

            lastname = fullname[0]
            firstname = fullname[1]

            patronymic = ""
            if len(fullname) > 2:
                patronymic = fullname[2]

            username = Client.translit("{}{}{}".format(lastname, firstname[0], patronymic[0] if len(patronymic) > 0 else ""))

            if not Client.objects.filter(username=username).exists():
                i += 1

                client = Client()
                client.lastname = lastname
                client.firstname = firstname
                client.patronymic = patronymic
                client.username = username
                client.save()

                try:
                    client_parameter = ClientParameter.objects.filter(username=username,
                                                                      attribute=CLEARTEXT_PASSWORD).get()
                except ObjectDoesNotExist:
                    client_parameter = ClientParameter()

                client_parameter.username = username
                client_parameter.attribute = CLEARTEXT_PASSWORD
                client_parameter.op = ":="
                client_parameter.value = password

                client_parameter.save()

        return render(request, 'panel/upload_file.html', {'count': i})
    else:
        return render(request, 'panel/upload_file.html')

