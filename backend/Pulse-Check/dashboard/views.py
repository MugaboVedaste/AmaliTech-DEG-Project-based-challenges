from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db import IntegrityError
from monitors.models import Monitor
from alerts.models import Alert
from django.utils import timezone
from monitors.serializers import MonitorCreateSerializer
from monitors.services.monitor_service import create_monitor, update_timeout
from monitors.services.timer_service import TIMERS, start_timer


def _redirect_after_action(request, device_id=None):
    next_url = request.POST.get('next')
    if next_url:
        return redirect(next_url)

    if device_id:
        return redirect('monitor_detail', device_id=device_id)

    return redirect('dashboard')


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

    unread_alert_count = Alert.objects.filter(
        monitor__user=user,
        is_read=False,
    ).count()
    
    context = {
        'monitors': monitors,
        'total_monitors': total_monitors,
        'active_count': active_count,
        'paused_count': paused_count,
        'down_count': down_count,
        'recent_alerts': recent_alerts,
        'unread_alert_count': unread_alert_count,
    }
    
    return render(request, 'dashboard/dashboard.html', context)


@login_required(login_url='/')
@require_POST
def register_monitor(request):
    serializer = MonitorCreateSerializer(data={
        'id': request.POST.get('device_id', '').strip(),
        'timeout': request.POST.get('timeout'),
        'alert_email': request.POST.get('alert_email', '').strip(),
    })

    if not serializer.is_valid():
        for error_list in serializer.errors.values():
            for error in error_list:
                messages.error(request, error)
        return _redirect_after_action(request)

    device_id = serializer.validated_data['id']

    if Monitor.objects.filter(device_id=device_id).exists():
        messages.error(request, f'Monitor {device_id} already exists.')
        return _redirect_after_action(request)

    try:
        monitor = create_monitor(user=request.user, data=serializer.validated_data)
    except IntegrityError:
        messages.error(request, f'Monitor {device_id} already exists.')
        return _redirect_after_action(request)

    messages.success(request, f'Monitor {monitor.device_id} created successfully.')
    return redirect('monitor_detail', device_id=monitor.device_id)


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
        'unread_alert_count': Alert.objects.filter(
            monitor__user=request.user,
            is_read=False,
        ).count(),
    }
    
    return render(request, 'dashboard/monitor_detail.html', context)


@login_required(login_url='/')
@require_POST
def pause_monitor(request, device_id):
    monitor = get_object_or_404(Monitor, device_id=device_id, user=request.user)
    monitor.status = 'PAUSED'
    monitor.save()

    if device_id in TIMERS:
        TIMERS[device_id].cancel()
        del TIMERS[device_id]

    messages.success(request, f'Monitor {device_id} paused.')
    return _redirect_after_action(request, device_id)


@login_required(login_url='/')
@require_POST
def resume_monitor(request, device_id):
    monitor = get_object_or_404(Monitor, device_id=device_id, user=request.user)
    monitor.status = 'ACTIVE'
    monitor.save()
    start_timer(monitor)

    messages.success(request, f'Monitor {device_id} resumed.')
    return _redirect_after_action(request, device_id)


@login_required(login_url='/')
@require_POST
def update_monitor_timeout(request, device_id):
    monitor = get_object_or_404(Monitor, device_id=device_id, user=request.user)
    timeout_value = request.POST.get('timeout', '').strip()

    if not timeout_value:
        messages.error(request, 'Timeout is required.')
        return _redirect_after_action(request, device_id)

    try:
        timeout = int(timeout_value)
    except ValueError:
        messages.error(request, 'Timeout must be a valid number.')
        return _redirect_after_action(request, device_id)

    if timeout < 1:
        messages.error(request, 'Timeout must be at least 1 second.')
        return _redirect_after_action(request, device_id)

    update_timeout(monitor, timeout)
    messages.success(request, f'Timeout for {device_id} updated to {timeout} seconds.')
    return _redirect_after_action(request, device_id)


@login_required(login_url='/')
def monitor_list(request):
    """List all monitors for the user"""
    monitors = Monitor.objects.filter(user=request.user).order_by('-updated_at')
    
    context = {
        'monitors': monitors,
        'unread_alert_count': Alert.objects.filter(
            monitor__user=request.user,
            is_read=False,
        ).count(),
    }
    
    return render(request, 'dashboard/monitor_list.html', context)


@login_required(login_url='/')
def alert_history(request):
    """View alert history"""
    alerts = Alert.objects.filter(
        monitor__user=request.user
    ).order_by('-created_at')[:50]

    Alert.objects.filter(
        monitor__user=request.user,
        is_read=False,
    ).update(is_read=True)
    
    context = {
        'alerts': alerts,
        'unread_alert_count': 0,
    }
    
    return render(request, 'dashboard/alert_history.html', context)
