from django.urls import path
from .views import (
    dashboard,
    monitor_detail,
    monitor_list,
    alert_history,
    register_monitor,
    pause_monitor,
    resume_monitor,
    update_monitor_timeout,
)

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('monitors/register/', register_monitor, name='dashboard_register_monitor'),
    path('monitors/', monitor_list, name='monitor_list'),
    path('monitors/<str:device_id>/', monitor_detail, name='monitor_detail'),
    path('monitors/<str:device_id>/pause/', pause_monitor, name='dashboard_pause_monitor'),
    path('monitors/<str:device_id>/resume/', resume_monitor, name='dashboard_resume_monitor'),
    path('monitors/<str:device_id>/timeout/', update_monitor_timeout, name='dashboard_update_timeout'),
    path('alerts/', alert_history, name='alert_history'),
]
