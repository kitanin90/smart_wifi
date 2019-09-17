from random import randint
import csv
import re

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
from .forms import FeedbackForm

from panel.const import CLEARTEXT_PASSWORD
from panel.models import Faculty, Client, Building, NAS, Session, ClientParameter, GroupReply, UserGroup, Feedback, \
    Group


@require_http_methods(["GET"])
@ensure_csrf_cookie
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
        username_login = '{}_{}'.format(username, password)
        user = authenticate(request, username=username_login, password=password)

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
        {"name": "employees", "title": "Сотрудники", "params": []}
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

            numberbook = row[6].rsplit('-')[0]

            if row[6] == '':
                continue

            lastname = fullname[0]
            firstname = fullname[1]

            name_group_bad = row[5].rsplit("-", 1)
            name_group = name_group_bad[1]

            patronymic = ""
            if len(fullname) > 2:
                patronymic = fullname[2]

            list_facultys = {
                'ИН': 'ФФ', 'РО': 'ФФ', 'ZМФО': 'ФФ', 'ZРЯ': 'ФФ', 'ZИН': 'ФФ', 'ZРО': 'ФФ', 'ZPO': 'ФФ', 'Журн': 'ФФ',
                'БИН': 'ФБиТЯ', 'ТЧИН': 'ФБиТЯ', 'ТЧО': 'ФБиТЯ', 'ZМСНП': 'ФБиТЯ', 'ZБРЯ': 'ФБиТЯ', 'ZТЧНО': 'ФБиТЯ',
                'ZБЯ': 'ФБиТЯ', 'ZТЧО': 'ФБиТЯ', 'БИС': 'ФБиТФ', 'БРЯ': 'ФБиТФ',
                'ИСТ': 'ИстФ', 'ZSТЕО': 'ИстФ', 'ZИСТ': 'ИстФ', 'ZМИСТ': 'ИстФ', 'ИСТО': 'ИстФ',
                'АР': 'ФМиИТ', 'АИС': 'ФМиИТ', 'МИ': 'ФМиИТ', 'МПМИ': 'ФМиИТ', 'МФ': 'ФМиИТ', 'ПИ': 'ФМиИТ',
                'ИНФ': 'ФМиИТ', 'ПМИ': 'ФМиИТ', 'ZSПИ': 'ФМиИТ', 'ZИНФ': 'ФМиИТ', 'ZММИ': 'ФМиИТ', 'OZМПМИ': 'ФМиИТ',
                'ZSПМИ': 'ФМиИТ', 'AP': 'ФМиИТ',
                'БИО': 'ЕНФ', 'МФИ': 'ЕНФ', 'ПРО': 'ЕНФ', 'ФИЗ': 'ЕНФ', 'ХИМ': 'ЕНФ', 'ХТ': 'ЕНФ', 'ФИ': 'ЕНФ',
                'ТБ': 'ЕНФ', 'БФ': 'ЕНФ', 'ТИ': 'ЕНФ', 'OZМБИ': 'ЕНФ', 'OZМХИМ': 'ЕНФ', 'ZSБИО': 'ЕНФ', 'ZSМС': 'ЕНФ',
                'ZSХТ': 'ЕНФ', 'ZМАШ': 'ЕНФ', 'ZПБ': 'ЕНФ', 'ZХТ': 'ЕНФ', 'OZМФИЗ': 'ЕНФ', 'OZМБИО': 'Корпус ЕНФ',
                'ZSПБ': 'ЕНФ', 'ZSМАШ': 'ЕНФ', 'ZSМФМ': 'ЕНФ', 'ZМТДО': 'ЕНФ', 'ZТ': 'ЕНФ', 'OZФПГНП': 'ЕНФ',
                'ZМФМ': 'ЕНФ', 'МФИЗ': 'ЕНФ', 'Т': 'ЕНФ', 'ZТТТ': 'ЕНФ',
                'НДО': 'ФПиП', 'ППО': 'ФПиП', 'НО': 'ФПиП', 'ZSДО': 'ФПиП', 'ZSНО': 'ФПиП', 'ZSППО': 'ФПиП',
                'ZДО': 'ФПиП', 'ZМНО': 'ФПиП', 'ZМППО': 'ФПиП', 'ZМРОО': 'ФПиП', 'ZНО': 'ФПиП', 'ZППО': 'ФПиП',
                'ZМДО': 'ФПиП', 'ZТИМПО': 'ФПиП', 'ZМУПК': 'ФПиП', 'ZмУК': 'ФПиП',
                'БУАА': 'ЭФ', 'ГМУ': 'ЭФ', 'ЭБ': 'ЭФ', 'ФК': 'ЭФ', 'ZSБУАА': 'ЭФ', 'ZSФК': 'ЭФ', 'ZБУАА': 'ЭФ',
                'ZУП': 'ЭФ', 'ZЭБ': 'ЭФ', 'ZЭКМ': 'ЭФ', 'ZЭП': 'ЭФ', 'ZГМУ': 'ЭФ', 'ZмЭП': 'ЭФ', 'УП': 'ЭФ',
                'ЭКМ': 'ЭФ', 'ЭП': 'ЭФ', 'ZИОТФ': 'ФБиТФ',
                'SГО': 'ЮФ', 'ГОС': 'ЮФ', 'ГРП': 'ЮФ', 'СПД': 'ЮФ', 'ЮПД': 'ЮФ', 'SГОС': 'ЮФ', 'OZSГОС': 'ЮФ',
                'OZSГРП': 'ЮФ', 'ZОГМВ': 'ЮФ', 'ZЮПД': 'ЮФ', 'OZГОС': 'ЮФ', 'OZГРП': 'ЮФ', 'ZSГОС': 'ЮФ',
                'ZПОГМВ': 'ЮФ', 'Экспл': 'Колледж', 'Мех': 'Колледж',
                'ZГРП': 'ЮФ', 'ZГОС': 'ЮФ', 'ZSГРП': 'ЮФ', 'ГС': 'Колледж', 'ПСО': 'Колледж', 'Э': 'Колледж',
                'ЭБД': 'Колледж', '2ГС': 'Колледж', '2ПСО': 'Колледж', '2ЭД': 'Колледж', '3БД': 'Колледж',
                '3ГС': 'Колледж', '3НО': 'Колледж', '3ПСО': 'Колледж', '2Э': 'Колледж', '3СА': 'Колледж',
                '3Ф': 'Колледж', '3Э': 'Колледж', '4НО': 'Колледж', 'Z3Э': 'Колледж', 'Z3ПСО': 'Колледж',
                'БД': 'Колледж', 'СА': 'Колледж', 'Ф': 'Колледж', 'ZПСО': 'Колледж', 'ZЭ': 'Колледж', 'ПСА': 'Колледж',
                'ZSАФК': 'СОП', 'ZФК': 'СОП', 'ZАФК': 'СОП', 'ZЯНРФ': 'СОП', 'ZОПИПО': 'СОП',
                'ZПН': 'СОП', 'ZРЛЗ': 'СОП', 'ZРЛ': 'СОП', 'ZОП': 'СОП', 'ZППС': 'СОП', 'БЯ': 'СОП', 'ТИМПО': 'СОП',
                'ТТТ': 'СОП',
                'ТЧР': 'Преподаватели', 'ЦИТ': 'ЦИТ'
            }

            list_building = {
                'ИН': 'Главный корпус', 'РО': 'Главный корпус', 'ZМФО': 'Главный корпус', 'ZРЯ': 'Главный корпус',
                'ZИН': 'Главный корпус', 'ZРО': 'Главный корпус', 'ZТЧО': 'Главный корпус', 'БИС': 'Главный корпус',
                'БИН': 'Главный корпус', 'ТЧИН': 'Главный корпус', 'ТЧО': 'Главный корпус', 'ZМСНП': 'Главный корпус',
                'ZБРЯ': 'Главный корпус', 'ZТЧНО': 'Главный корпус', 'БРЯ': 'Главный корпус', 'ZPO': 'Главный корпус',
                'ZБЯ': 'Главный корпус', 'ИСТО': 'Главный корпус', 'ZИОТФ': 'Главный корпус', 'Журн': 'Главный корпус',
                'ИСТ': 'Главный корпус', 'ZSТЕО': 'Главный корпус', 'ZИСТ': 'Главный корпус', 'ZМИСТ': 'Главный корпус',
                'АР': 'Корпус ФМиИТ', 'АИС': 'Корпус ФМиИТ', 'МИ': 'Корпус ФМиИТ', 'МПМИ': 'Корпус ФМиИТ',
                'МФ': 'Корпус ФМиИТ', 'ПИ': 'Корпус ФМиИТ', 'AP': 'Корпус ФМиИТ',
                'ИНФ': 'Корпус ФМиИТ', 'ПМИ': 'Корпус ФМиИТ', 'ZSПИ': 'Корпус ФМиИТ', 'ZИНФ': 'Корпус ФМиИТ',
                'ZММИ': 'Корпус ФМиИТ', 'OZМПМИ': 'Корпус ФМиИТ',
                'ZSПМИ': 'Корпус ФМиИТ',
                'БИО': 'Корпус ЕНФ', 'МФИ': 'Корпус ЕНФ', 'ПРО': 'Корпус ЕНФ', 'ФИЗ': 'Корпус ЕНФ', 'ХИМ': 'Корпус ЕНФ',
                'ХТ': 'Корпус ЕНФ', 'ФИ': 'Корпус ЕНФ', 'OZМБИО': 'Корпус ЕНФ', 'OZФПГНП': 'Корпус ЕНФ',
                'ТБ': 'Корпус ЕНФ', 'БФ': 'Корпус ЕНФ', 'ТИ': 'Корпус ЕНФ', 'OZМБИ': 'Корпус ЕНФ', 'ZМФМ': 'Корпус ЕНФ',
                'OZМХИМ': 'Корпус ЕНФ', 'ZSБИО': 'Корпус ЕНФ', 'ZSМС': 'Корпус ЕНФ', 'Т': 'Корпус ЕНФ',
                'ZSХТ': 'Корпус ЕНФ', 'ZМАШ': 'Корпус ЕНФ', 'ZПБ': 'Корпус ЕНФ', 'ZХТ': 'Корпус ЕНФ',
                'OZМФИЗ': 'Корпус ЕНФ', 'МФИЗ': 'Корпус ЕНФ',
                'ZSПБ': 'Корпус ЕНФ', 'ZSМАШ': 'Корпус ЕНФ', 'ZSМФМ': 'Корпус ЕНФ', 'ZМТДО': 'Корпус ЕНФ',
                'ZТ': 'Корпус ЕНФ', 'ZТТТ': 'Корпус ЕНФ',
                'НДО': 'Корпус ФПиП', 'ППО': 'Корпус ФПиП', 'НО': 'Корпус ФПиП', 'ZSДО': 'Корпус ФПиП',
                'ZSНО': 'Корпус ФПиП', 'ZSППО': 'Корпус ФПиП', 'ZмУК': 'Корпус ФПиП',
                'ZДО': 'Корпус ФПиП', 'ZМНО': 'Корпус ФПиП', 'ZМППО': 'Корпус ФПиП', 'ZМРОО': 'Корпус ФПиП',
                'ZНО': 'Корпус ФПиП', 'ZППО': 'Корпус ФПиП',
                'ZМДО': 'Корпус ФПиП', 'ZТИМПО': 'Корпус ФПиП', 'ZМУПК': 'Корпус ФПиП',
                'БУАА': 'Корпус ЭФ', 'ГМУ': 'Корпус ЭФ', 'ЭБ': 'Корпус ЭФ', 'ФК': 'Корпус ЭФ', 'ZSБУАА': 'Корпус ЭФ',
                'ZSФК': 'Корпус ЭФ', 'ZБУАА': 'Корпус ЭФ', 'ZГМУ': 'Корпус ЭФ', 'ZмЭП': 'Корпус ЭФ', 'ЭКМ': 'Корпус ЭФ',
                'ZУП': 'Корпус ЭФ', 'ZЭБ': 'Корпус ЭФ', 'ZЭКМ': 'Корпус ЭФ', 'ZЭП': 'Корпус ЭФ', 'УП': 'Корпус ЭФ',
                'ЭП': 'Корпус ЭФ',
                'SГО': 'Корпус ЮФ', 'ГОС': 'Корпус ЮФ', 'ГРП': 'Корпус ЮФ', 'СПД': 'Корпус ЮФ', 'ЮПД': 'Корпус ЮФ',
                'SГОС': 'Корпус ЮФ', 'OZSГОС': 'Корпус ЮФ', 'ZПОГМВ': 'Корпус ЮФ',
                'OZSГРП': 'Корпус ЮФ', 'ZОГМВ': 'Корпус ЮФ', 'ZЮПД': 'Корпус ЮФ', 'OZГОС': 'Корпус ЮФ',
                'OZГРП': 'Корпус ЮФ', 'ZSГОС': 'Корпус ЮФ', 'Мех': 'Корпус Колледжа',
                'ZГРП': 'Корпус ЮФ', 'ZГОС': 'Корпус ЮФ', 'ZSГРП': 'Корпус ЮФ', 'Экспл': 'Корпус Колледжа',
                'ЭБД': 'Корпус Колледжа', '2ГС': 'Корпус Колледжа', '2ПСО': 'Корпус Колледжа', '2ЭД': 'Корпус Колледжа',
                '3БД': 'Корпус Колледжа', 'ГС': 'Корпус Колледжа', 'ПСО': 'Корпус Колледжа', 'Э': 'Корпус Колледжа',
                '3ГС': 'Корпус Колледжа', '3НО': 'Корпус Колледжа', '3ПСО': 'Корпус Колледжа', '2Э': 'Корпус Колледжа',
                '3СА': 'Корпус Колледжа', 'БД': 'Корпус Колледжа', 'ZПСО': 'Корпус Колледжа', 'ZЭ': 'Корпус Колледжа',
                '3Ф': 'Корпус Колледжа', '3Э': 'Корпус Колледжа', '4НО': 'Корпус Колледжа', 'Z3Э': 'Корпус Колледжа',
                'Z3ПСО': 'Корпус Колледжа', 'СА': 'Корпус Колледжа', 'Ф': 'Корпус Колледжа', 'ПСА': 'Корпус Колледжа',
                'ZSАФК': 'СОП', 'ZАФК': 'СОП', 'ZФК': 'СОП', 'ZЯНРФ': 'СОП', 'ZОПИПО': 'СОП', 'БЯ': 'СОП',
                'ZПН': 'СОП', 'ZРЛЗ': 'СОП', 'ZРЛ': 'СОП', 'ZОП': 'СОП', 'ZППС': 'СОП', 'ТИМПО': 'СОП', 'ТТТ': 'СОП',
                'ТЧР': 'Все Преподаватели', 'ЦИТ': 'Отдел ЦИТ'

            }

            list_address = {
                'Главный корпус': 'Пр.Ленина, д.49',
                'Корпус ФМиИТ': 'Пр.Ленина, д.37',
                'Корпус ФПиП': 'Комсомольская 67/1',
                'Корпус ЭФ': 'Гоголя 147',
                'Корпус ЮФ': 'Пр.Ленина, д.47а',
                'Корпус Колледжа': 'Элеваторная 80',
                'СОП': 'Пр.Ленина, д.49',
                'Корпус ЕНФ': 'Пр.Ленина, д.49а',
                'Все Преподаватели': 'Пр.Ленина, д.49а',
                'Отдел ЦИТ': 'Пр.Ленина, д.49а',
            }

            # group_in_csv
            group_in_csv = re.sub(r"\d+", "", name_group, flags=re.UNICODE)  # Удаляет символы из строки

            password = ClientParameter.translit_pass("{}".format(numberbook))

            full = Client.translit(
                "{}{}{}".format(lastname, firstname[0], patronymic[0] if len(patronymic) > 0 else " "))

            username = Client.translit(
                "{}_{}".format(full, password)
            )

            if group_in_csv in list_building:
                if not Building.objects.filter(name=list_building[group_in_csv]):
                    build = Building()
                    build.name = list_building[group_in_csv]
                    build.address = list_address[build.name]
                    build.save()

                if not Faculty.objects.filter(name=list_facultys[group_in_csv]):
                    faculty = Faculty()
                    faculty.name = list_facultys[group_in_csv]
                    faculty.building = Building.objects.get(name=list_building[group_in_csv])
                    faculty.save()

            if not Client.objects.filter(username=username).exists():
                i += 1

                client = Client()
                client.lastname = lastname
                client.firstname = firstname
                client.patronymic = patronymic
                client.username = username
                if group_in_csv == 'ТЧР':
                    client.status = 'Преподаватель'
                elif group_in_csv == 'ЦИТ':
                    client.status = 'Сотрудник ЦИТа'
                else:
                    client.status = 'Студент'
                client.faculty = Faculty.objects.get(name=list_facultys[group_in_csv])
                client.group = Group.objects.get_or_create(name=group_in_csv)[0]
                client.save()

                try:
                    client_parameter = ClientParameter.objects.filter(username=username,
                                                                      attribute=CLEARTEXT_PASSWORD,
                                                                      value=password).get()
                except ObjectDoesNotExist:
                    client_parameter = ClientParameter()

                client_parameter.username = username
                client_parameter.attribute = CLEARTEXT_PASSWORD
                client_parameter.op = ":="
                client_parameter.value = password
                client_parameter.save()
            else:
                if Client.objects.filter(username=username):
                    continue




        return render(request, 'panel/upload_file.html', {'count': i})
    else:
        return render(request, 'panel/upload_file.html')
