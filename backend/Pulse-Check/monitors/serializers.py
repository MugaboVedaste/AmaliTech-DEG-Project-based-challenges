from rest_framework import serializers


class MonitorCreateSerializer(serializers.Serializer):
    id = serializers.CharField()
    timeout = serializers.IntegerField()
    alert_email = serializers.EmailField()