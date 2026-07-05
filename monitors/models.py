from django.db import models
from django.conf import settings


class Monitor(models.Model):

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('PAUSED', 'Paused'),
        ('DOWN', 'Down'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='monitors')

    device_id = models.CharField(max_length=100, unique=True)

    timeout = models.IntegerField(default=60)

    alert_email = models.EmailField()

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')

    last_heartbeat = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.device_id