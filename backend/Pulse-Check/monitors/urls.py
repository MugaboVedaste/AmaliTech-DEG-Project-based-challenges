from django.urls import path
from .views import (
    monitor_heartbeat,
    register_monitor,
    pause_monitor,
    resume_monitor,
    list_monitors,
    update_monitor_timeout

)

urlpatterns = [
    path("<str:device_id>/heartbeat/", monitor_heartbeat),
    path("", register_monitor),
    path("list/", list_monitors),
    path("<str:device_id>/pause/", pause_monitor),
    path("<str:device_id>/resume/", resume_monitor),
    path("<str:device_id>/timeout/", update_monitor_timeout),
]