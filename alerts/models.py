from django.db import models
from django.utils import timezone
from monitors.models import Monitor


class Alert(models.Model):

    ALERT_TYPES = [
        ('DOWN', 'Device Down'),
        ('RECOVERY', 'Device Recovered'),
    ]

    monitor = models.ForeignKey(Monitor, on_delete=models.CASCADE, related_name='alerts')

    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)

    message = models.TextField()

    is_resolved = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.monitor.device_id} - {self.alert_type}"