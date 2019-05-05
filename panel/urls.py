from django.urls import path

from . import views

urlpatterns = [
    path('', views.connect, name='connect'),
    path('successful', views.successful_connect, name='successful_connect'),
]
