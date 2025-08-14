import json
import time

from django.db import connection

from .models import NotificationLog


def smart_notify(channel_name, payload_data=None):
    """
    Send a PostgreSQL NOTIFY with persistence for guaranteed delivery.

    Args:
        channel_name (str): The PostgreSQL channel to notify on
        payload_data (dict, optional): The data to send. Defaults to {}.

    Returns:
        int: The notification log ID

    Raises:
        Exception: If the notification fails to send
    """
    if payload_data is None:
        payload_data = {}

    # Create notification log entry
    log_entry = NotificationLog.objects.create(channel=channel_name, payload=payload_data)

    # Build notification payload with notification log ID
    notification_payload = {
        'notification_log_id': log_entry.id,
        'timestamp': time.time(),
        'data': payload_data,
    }

    # Check if payload is too large (PostgreSQL NOTIFY limit is ~8KB)
    payload_json = json.dumps(notification_payload)
    if len(payload_json.encode('utf-8')) > 7500:  # Leave some buffer
        # Send minimal notification for large payloads
        notification_payload = {
            'notification_log_id': log_entry.id,
            'timestamp': time.time(),
            'large_payload': True,
        }
        payload_json = json.dumps(notification_payload)

    # Send the notification
    with connection.cursor() as cursor:
        cursor.execute('SELECT pg_notify(%s, %s)', [channel_name, payload_json])

    return log_entry.id


def cleanup_old_notifications(days_to_keep=7):
    """
    Remove old notification logs to prevent table bloat.

    Args:
        days_to_keep (int): Number of days to retain notifications

    Returns:
        int: Number of notifications deleted
    """
    return NotificationLog.cleanup_old(days_to_keep)


def create_trigger_for_table(table_name, channel_name='data_change'):
    """
    Create a trigger on a table to send notifications on changes.

    Args:
        table_name (str): Name of the table to add trigger to
        channel_name (str): PostgreSQL channel to notify on

    Returns:
        str: SQL command to create the trigger
    """
    trigger_name = f'notify_{table_name}_changes'

    return f"""
    CREATE TRIGGER {trigger_name}
        AFTER INSERT OR UPDATE OR DELETE ON {table_name}
        FOR EACH ROW EXECUTE FUNCTION notify_data_change();
    """
