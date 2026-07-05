from django.urls import path
from .views import monitor_heartbeat

urlpatterns = [
    path("<str:device_id>/heartbeat/", monitor_heartbeat),
]