import threading
from django.utils import timezone
from alerts.models import Alert

# store timers in memory
TIMERS = {}

def start_timer(monitor):

    device_id = monitor.device_id

    # cancel old timer if exists
    if device_id in TIMERS:
        TIMERS[device_id].cancel()

    # create new timer
    timer = threading.Timer(
        monitor.timeout,
        trigger_alert,
        [monitor.id]
    )

    TIMERS[device_id] = timer
    timer.start()

def trigger_alert(monitor_id):

    from monitors.models import Monitor

    try:
        monitor = Monitor.objects.get(id=monitor_id)
    except Monitor.DoesNotExist:
        return

    monitor.status = "DOWN"
    monitor.save()

    Alert.objects.create(
        monitor=monitor,
        alert_type="DOWN",
        message=f"Device {monitor.device_id} is DOWN!",
        created_at=timezone.now()
    )

    print({
        "ALERT": f"Device {monitor.device_id} is down!",
        "time": str(timezone.now())
    })