from rest_framework import serializers
from .models import Alert


class AlertSerializer(serializers.ModelSerializer):
    device_id = serializers.CharField(source='monitor.device_id', read_only=True)

    class Meta:
        model = Alert
        fields = ['id', 'device_id', 'alert_type', 'message', 'is_resolved', 'is_read', 'created_at']
