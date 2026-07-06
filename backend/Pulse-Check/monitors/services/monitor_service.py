from monitors.models import Monitor
from .timer_service import start_timer
from django.utils import timezone

def create_monitor(user, data):

    monitor = Monitor.objects.create(
        user=user,
        device_id=data["id"],
        timeout=data["timeout"],
        alert_email=data["alert_email"],
        status="ACTIVE",
        last_heartbeat=None
    )

    # start countdown immediately
    start_timer(monitor)

    return monitor
def heartbeat(monitor):

    # device is alive, mark as active and reset timeout
    monitor.last_heartbeat = timezone.now()
    monitor.status = "ACTIVE"
    monitor.save()

    # reset timer
    start_timer(monitor)

    return monitor
def update_timeout(monitor, new_timeout):

    monitor.timeout = new_timeout
    monitor.save()

    # restart timer with new timeout
    start_timer(monitor)

    return monitor