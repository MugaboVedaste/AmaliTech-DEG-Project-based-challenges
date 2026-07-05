from rest_framework.decorators import api_view
from rest_framework.response import Response
from monitors.models import Monitor
from monitors.services.monitor_service import heartbeat

@api_view(['POST'])
def monitor_heartbeat(request, device_id):

    try:
        monitor = Monitor.objects.get(device_id=device_id)
    except Monitor.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    monitor = heartbeat(monitor)

    return Response({
        "message": "Heartbeat received",
        "status": monitor.status
    })
