from django.urls import path
from .views import list_alerts, device_alerts, resolve_alert

urlpatterns = [
    path('resolve/<int:alert_id>/', resolve_alert),
    path('<str:device_id>/', device_alerts),
    path('', list_alerts),
]
