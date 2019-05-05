from django.shortcuts import render
from django.views.decorators.http import require_http_methods


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
def index(request):
    return render(request, 'panel/index.html')


@require_http_methods(["GET"])
def info(request):
    return render(request, 'panel/info.html')


@require_http_methods(["GET"])
def point(request):
    return render(request, 'panel/point.html')


@require_http_methods(["GET"])
def users(request):
    return render(request, 'panel/users.html')
