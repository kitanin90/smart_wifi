from django.urls import path

from . import views
from . import dashboard
from django.views.defaults import server_error, page_not_found, permission_denied
from .views import *

urlpatterns = [
    path('', views.connect, name='connect'),
    path('successful', views.successful_connect, name='successful_connect'),
    path('sendfeedback', FeedbackCreate.as_view(), name='feedback_create_url'),

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

    # Settings
    path('panel/settings', views.settings, name='settings'),

    # Feedback
    path('panel/feedback_list', views.feedbacks_list, name='feedbacks_list'),

    path('panel/upload_file', views.upload_file, name='contact_upload'),

    # Error

]
