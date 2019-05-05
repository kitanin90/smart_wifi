from django.urls import path

from . import views

urlpatterns = [
    path('', views.connect, name='connect'),
    path('successful', views.successful_connect, name='successful_connect'),

    path('panel/auth', views.auth, name='auth'),
    path('panel', views.index, name='index'),
    path('panel/info', views.info, name='info'),
    path('panel/point', views.point, name='point'),
    path('panel/users', views.users, name='users'),
]
