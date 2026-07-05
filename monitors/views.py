from rest_framework.decorators import api_view
from rest_framework.response import Response
from monitors.models import Monitor
from monitors.services.monitor_service import heartbeat, create_monitor
from monitors.services.timer_service import start_timer
from monitors.serializers import MonitorCreateSerializer
from monitors.services.timer_service import TIMERS
from rest_framework.permissions import IsAuthenticated

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
@api_view(['POST'])
def register_monitor(request):

    serializer = MonitorCreateSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    monitor = create_monitor(
        user=request.user,
        data=serializer.validated_data
    )

    return Response({
        "message": "Monitor created",
        "device_id": monitor.device_id,
        "status": monitor.status
    }, status=201)

@api_view(['POST'])
def pause_monitor(request, device_id):

    try:
        monitor = Monitor.objects.get(device_id=device_id)
    except Monitor.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    monitor.status = "PAUSED"
    monitor.save()

    # stop timer
    if device_id in TIMERS:
        TIMERS[device_id].cancel()

    return Response({
        "message": "Monitor paused",
        "status": monitor.status
    })

@api_view(['POST'])
def resume_monitor(request, device_id):

    try:
        monitor = Monitor.objects.get(device_id=device_id)
    except Monitor.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    monitor.status = "ACTIVE"
    monitor.save()

    # restart timer
    start_timer(monitor)

    return Response({
        "message": "Monitor resumed",
        "status": monitor.status
    })

@api_view(['GET'])
def list_monitors(request):

    monitors = Monitor.objects.filter(user=request.user)

    data = []

    for m in monitors:
        data.append({
            "device_id": m.device_id,
            "status": m.status,
            "timeout": m.timeout,
            "last_heartbeat": m.last_heartbeat,
        })

    return Response(data)

@api_view(['POST'])
def register_monitor(request):

    if not request.user.is_authenticated:
        return Response({"error": "Unauthorized"}, status=401)
