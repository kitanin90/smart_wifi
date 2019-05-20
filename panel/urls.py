from django.urls import path

from . import views
from . import dashboard

urlpatterns = [
    path('', views.connect, name='connect'),
    path('successful', views.successful_connect, name='successful_connect'),

    path('panel/auth', views.auth, name='auth'),
    path('panel/logout', views.logout_view, name='logout'),

    # Dashboard
    path('panel/', dashboard.index, name='dashboard'),

    # Point
    path('panel/points', views.points, name='points'),
    path('panel/point/<int:nas_id>', views.point, name='point'),

    # Users
    path('panel/clients', views.clients, name='clients'),
    path('panel/clients/<int:client_id>', views.client, name='client'),

    # Session
    path('panel/session/<int:session_id>', views.session, name='session'),

    # Report
    path('panel/report', views.report, name='report'),
]
