from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from monitors.models import Monitor
from alerts.models import Alert
from alerts.serializers import AlertSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_alerts(request):

    alerts = Alert.objects.filter(monitor__user=request.user).order_by('-created_at')

    return Response(AlertSerializer(alerts, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def device_alerts(request, device_id):

    try:
        monitor = Monitor.objects.get(device_id=device_id, user=request.user)
    except Monitor.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    alerts = Alert.objects.filter(monitor=monitor).order_by('-created_at')

    return Response(AlertSerializer(alerts, many=True).data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def resolve_alert(request, alert_id):

    try:
        alert = Alert.objects.get(id=alert_id, monitor__user=request.user)
    except Alert.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    alert.is_resolved = True
    alert.save()

    return Response({
        "message": "Alert resolved",
        "id": alert.id,
        "is_resolved": alert.is_resolved
    })
