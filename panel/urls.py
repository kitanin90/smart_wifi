from django.urls import path

from . import views

urlpatterns = [
    path('', views.connect, name='connect'),
    path('successful', views.successful_connect, name='successful_connect'),

    path('panel/auth', views.auth, name='auth'),
    path('panel', views.index, name='index'),

    # Point
    path('panel/point', views.point, name='point'),
    path('panel/nas/<int:nas_id>', views.nas, name='nas'),

    # Users
    path('panel/clients', views.clients, name='clients'),
    path('panel/clients/<int:client_id>', views.client, name='client'),

    # Dashboard
    path('panel/dashboard', views.dashboard, name='dashboard'),
]
