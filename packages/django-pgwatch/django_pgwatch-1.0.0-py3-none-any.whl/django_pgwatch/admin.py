from django.contrib import admin, messages
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from .models import NotificationLog
from .utils import cleanup_old_notifications


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'channel',
        'created_at',
        'payload_preview',
        'consumer_count',
        'payload_size_display',
    ]

    list_filter = [
        'channel',
        'created_at',
    ]

    search_fields = [
        'channel',
        'payload',
    ]

    readonly_fields = [
        'id',
        'channel',
        'payload',
        'created_at',
        'processed_by',
        'payload_size_display',
        'consumer_list',
    ]

    ordering = ['-created_at']

    list_per_page = 50

    actions = [
        'cleanup_selected',
        'reprocess_notifications',
    ]

    fieldsets = (
        (
            'Notification Info',
            {'fields': ('id', 'channel', 'created_at', 'payload_size_display')},
        ),
        ('Payload Data', {'fields': ('payload',), 'classes': ('collapse',)}),
        (
            'Processing Info',
            {'fields': ('processed_by', 'consumer_list'), 'classes': ('collapse',)},
        ),
    )

    def payload_preview(self, obj):
        """Show a truncated preview of the payload."""
        payload_str = str(obj.payload)
        if len(payload_str) > 100:
            return format_html(
                '<code title="{}">{}&hellip;</code>', payload_str, payload_str[:100]
            )
        return format_html('<code>{}</code>', payload_str)

    payload_preview.short_description = 'Payload Preview'

    def consumer_count(self, obj):
        """Show how many consumers have processed this notification."""
        count = len(obj.processed_by)
        if count == 0:
            return format_html('<span style="color: red;">0</span>')
        return count

    consumer_count.short_description = 'Consumers'

    def payload_size_display(self, obj):
        """Display payload size in human-readable format."""
        size = obj.payload_size
        if size < 1024:
            return f'{size} bytes'
        elif size < 1024 * 1024:
            return f'{size / 1024:.1f} KB'
        else:
            return f'{size / (1024 * 1024):.1f} MB'

    payload_size_display.short_description = 'Payload Size'

    def consumer_list(self, obj):
        """Display list of consumers that processed this notification."""
        if not obj.processed_by:
            return format_html('<em>None</em>')

        consumers = ', '.join(obj.processed_by)
        return format_html('<code>{}</code>', consumers)

    consumer_list.short_description = 'Processed By'

    def get_queryset(self, request):
        """Optimize queryset for admin list view."""
        return super().get_queryset(request).select_related()

    def cleanup_selected(self, request, queryset):
        """Admin action to delete selected notifications."""
        count = queryset.count()
        queryset.delete()

        self.message_user(
            request, f'Successfully deleted {count} notification logs.', messages.SUCCESS
        )

    cleanup_selected.short_description = 'Delete selected notification logs'

    def reprocess_notifications(self, request, queryset):
        """Admin action to mark notifications for reprocessing."""
        count = 0
        for notification in queryset:
            notification.processed_by = []
            notification.save(update_fields=['processed_by'])
            count += 1

        self.message_user(
            request,
            f'Marked {count} notifications for reprocessing (cleared consumer lists).',
            messages.SUCCESS,
        )

    reprocess_notifications.short_description = (
        'Mark for reprocessing (clear consumer lists)'
    )

    def changelist_view(self, request, extra_context=None):
        """Add summary statistics to the changelist view."""
        extra_context = extra_context or {}

        # Get summary statistics
        total_notifications = NotificationLog.objects.count()

        # Notifications by channel
        channel_stats = (
            NotificationLog.objects.values('channel')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        # Recent notifications (last 24 hours)
        last_24h = timezone.now() - timezone.timedelta(hours=24)
        recent_count = NotificationLog.objects.filter(created_at__gte=last_24h).count()

        # Unprocessed notifications
        unprocessed_count = NotificationLog.objects.filter(processed_by=[]).count()

        extra_context.update(
            {
                'total_notifications': total_notifications,
                'channel_stats': list(channel_stats[:10]),  # Top 10 channels
                'recent_count': recent_count,
                'unprocessed_count': unprocessed_count,
            }
        )

        return super().changelist_view(request, extra_context)


# Add a custom admin view for cleanup operations
class CleanupView:
    """Custom admin view for notification cleanup operations."""

    def cleanup_old_notifications_view(self, request):
        """Admin view to cleanup old notifications."""
        if request.method == 'POST':
            days = int(request.POST.get('days', 7))
            deleted_count = cleanup_old_notifications(days)

            messages.success(
                request,
                f'Successfully cleaned up {deleted_count} notifications '
                f'older than {days} days.',
            )

            return HttpResponseRedirect(
                reverse('admin:django_pgwatch_notificationlog_changelist')
            )

        # For GET requests, redirect to changelist
        return HttpResponseRedirect(
            reverse('admin:django_pgwatch_notificationlog_changelist')
        )
