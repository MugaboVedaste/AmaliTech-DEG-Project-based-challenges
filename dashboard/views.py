from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from monitors.models import Monitor
from alerts.models import Alert
from django.utils import timezone
from datetime import timedelta


@login_required(login_url='/')
def dashboard(request):
    """Main dashboard view showing monitor overview"""
    user = request.user
    monitors = Monitor.objects.filter(user=user).order_by('-updated_at')
    
    # Calculate stats
    total_monitors = monitors.count()
    active_count = monitors.filter(status='ACTIVE').count()
    paused_count = monitors.filter(status='PAUSED').count()
    down_count = monitors.filter(status='DOWN').count()
    
    # Get recent alerts
    recent_alerts = Alert.objects.filter(
        monitor__user=user
    ).order_by('-created_at')[:10]
    
    context = {
        'monitors': monitors,
        'total_monitors': total_monitors,
        'active_count': active_count,
        'paused_count': paused_count,
        'down_count': down_count,
        'recent_alerts': recent_alerts,
    }
    
    return render(request, 'dashboard/dashboard.html', context)


@login_required(login_url='/')
def monitor_detail(request, device_id):
    """View details for a specific monitor"""
    try:
        monitor = Monitor.objects.get(device_id=device_id, user=request.user)
    except Monitor.DoesNotExist:
        return render(request, 'dashboard/404.html', status=404)
    
    # Get alerts for this monitor
    alerts = Alert.objects.filter(monitor=monitor).order_by('-created_at')[:20]
    
    # Time since last heartbeat
    if monitor.last_heartbeat:
        time_since_heartbeat = timezone.now() - monitor.last_heartbeat
    else:
        time_since_heartbeat = None
    
    context = {
        'monitor': monitor,
        'alerts': alerts,
        'time_since_heartbeat': time_since_heartbeat,
    }
    
    return render(request, 'dashboard/monitor_detail.html', context)


@login_required(login_url='/')
def monitor_list(request):
    """List all monitors for the user"""
    monitors = Monitor.objects.filter(user=request.user).order_by('-updated_at')
    
    context = {
        'monitors': monitors,
    }
    
    return render(request, 'dashboard/monitor_list.html', context)


@login_required(login_url='/')
def alert_history(request):
    """View alert history"""
    alerts = Alert.objects.filter(
        monitor__user=request.user
    ).order_by('-created_at')[:50]
    
    context = {
        'alerts': alerts,
    }
    
    return render(request, 'dashboard/alert_history.html', context)
