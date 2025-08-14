import json

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone


class NotificationLog(models.Model):
    """
    Persistent storage for PostgreSQL NOTIFY payloads.
    Enables playback of missed notifications for disconnected consumers.
    """

    channel = models.CharField(
        max_length=100,
        db_index=True,
        help_text='PostgreSQL channel name',
    )

    payload = models.JSONField(help_text='Notification payload data')

    created_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text='When the notification was created',
    )

    processed_by = ArrayField(
        models.CharField(max_length=255),
        default=list,
        help_text='List of consumer IDs that have processed this notification',
    )

    class Meta:
        indexes = [
            models.Index(fields=['channel', 'id']),
        ]
        ordering = ['id']

    def __str__(self):
        return f'Notification {self.id} on {self.channel}'

    def add_processed_by(self, consumer_id):
        """Add a consumer ID to the processed list if not already present."""
        if consumer_id not in self.processed_by:
            self.processed_by.append(consumer_id)
            self.save(update_fields=['processed_by'])

    def is_processed_by(self, consumer_id):
        """Check if this notification was processed by a specific consumer."""
        return consumer_id in self.processed_by

    @property
    def payload_size(self):
        """Get the size of the payload in bytes."""
        return len(json.dumps(self.payload).encode('utf-8'))

    @classmethod
    def get_unprocessed_for_consumer(cls, consumer_id, channel=None, since_id=0):
        """Get notifications that haven't been processed by a specific consumer."""
        queryset = cls.objects.filter(id__gt=since_id).exclude(
            processed_by__contains=[consumer_id]
        )

        if channel:
            queryset = queryset.filter(channel=channel)

        return queryset.order_by('id')

    @classmethod
    def get_last_processed_id(cls, consumer_id, channel):
        """Get the highest ID processed by a consumer for a channel."""
        result = cls.objects.filter(
            channel=channel, processed_by__contains=[consumer_id]
        ).aggregate(max_id=models.Max('id'))
        return result['max_id'] or 0

    @classmethod
    def cleanup_old(cls, days_to_keep=7):
        """Remove old notification logs."""
        cutoff_date = timezone.now() - timezone.timedelta(days=days_to_keep)
        deleted_count, _ = cls.objects.filter(created_at__lt=cutoff_date).delete()
        return deleted_count
