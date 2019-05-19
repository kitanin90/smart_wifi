from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from panel.models import Faculty, Client, Building, NAS


@require_http_methods(["GET"])
def connect(request):
    return render(request, 'captive/index.html')


@require_http_methods(["GET"])
def successful_connect(request):
    return render(request, 'captive/successful.html')


@require_http_methods(["GET"])
def auth(request):
    return render(request, 'panel/auth.html')


@require_http_methods(["GET"])
def points(request):
    building_list = Building.objects.all()
    nas_list = None

    if "building_id" in request.GET:
        building_id = request.GET["building_id"]
        building = Building.objects.get(id=building_id)
        nas_list = NAS.objects.filter(building=building)

    return render(request, 'panel/points.html', {"building_list": building_list, "nas_list": nas_list})


@require_http_methods(["GET"])
def point(request, nas_id):
    nas = NAS.objects.get(id=nas_id)

    return render(request, 'panel/point.html', {"nas": nas})


@require_http_methods(["GET"])
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
def client(request, client_id):
    client = Client.objects.get(id=client_id)

    return render(request, 'panel/client.html', {"client": client})
