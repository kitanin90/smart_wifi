from django.shortcuts import render
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def connect(request):
    return render(request, 'captive/index.html')


@require_http_methods(["GET"])
def successful_connect(request):
    return render(request, 'captive/successful.html')
