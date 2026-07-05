from django.urls import path
from .views import dashboard, monitor_detail, monitor_list, alert_history

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('monitors/', monitor_list, name='monitor_list'),
    path('monitors/<str:device_id>/', monitor_detail, name='monitor_detail'),
    path('alerts/', alert_history, name='alert_history'),
]
