"""
Example consumer implementations for django-pgwatch.
"""

import logging
import time
from typing import Any, Dict

from .consumer import BaseConsumer, NotificationHandler
from .utils import smart_notify

logger = logging.getLogger(__name__)


class DatabaseChangeConsumer(BaseConsumer):
    """
    Example consumer that handles database change notifications.
    Processes INSERT, UPDATE, DELETE operations on any table.
    """

    def handle_notification(self, handler: NotificationHandler):
        """Handle database change notifications."""
        action_type = 'REPLAY' if handler.is_replay else 'REAL-TIME'

        self.stdout_write(
            f'[{action_type}] Processing notification {handler.notification_log_id}'
        )
        self.stdout_write(f'  Table: {handler.get_table()}')
        self.stdout_write(f'  Action: {handler.get_action()}')
        self.stdout_write(f'  Record ID: {handler.get_record_id()}')

        # Route to specific handlers based on table
        table = handler.get_table()
        if table == 'users':
            self.handle_user_change(handler)
        elif table == 'orders':
            self.handle_order_change(handler)
        elif table == 'products':
            self.handle_product_change(handler)
        else:
            self.handle_generic_change(handler)

    def handle_user_change(self, handler: NotificationHandler):
        """Handle user table changes."""
        if handler.is_insert():
            new_data = handler.get_new_data()
            logger.info(
                f'New user created: {new_data.get("email")}'
                f' (ID: {handler.get_record_id()})'
            )
            # Example: Send welcome email, create user profile, etc.

        elif handler.is_update():
            old_data = handler.get_old_data()
            new_data = handler.get_new_data()

            # Check for email changes
            if old_data.get('email') != new_data.get('email'):
                logger.info(
                    f'User email changed: {old_data.get("email")}'
                    f' -> {new_data.get("email")}'
                )
                # Example: Update external systems, send confirmation email

            # Check for status changes
            if old_data.get('is_active') != new_data.get('is_active'):
                status = 'activated' if new_data.get('is_active') else 'deactivated'
                logger.info(f'User {status}: {new_data.get("email")}')
                # Example: Update permissions, send notification

        elif handler.is_delete():
            old_data = handler.get_old_data()
            logger.info(
                f'User deleted: {old_data.get("email")} (ID: {handler.get_record_id()})'
            )
            # Example: Cleanup related data, send deletion confirmation

    def handle_order_change(self, handler: NotificationHandler):
        """Handle order table changes."""
        if handler.is_insert():
            new_data = handler.get_new_data()
            logger.info(
                f'New order created: #{new_data.get("order_number")}'
                f' for user {new_data.get("user_id")}'
            )
            # Example: Send order confirmation, update inventory, process payment

        elif handler.is_update():
            old_data = handler.get_old_data()
            new_data = handler.get_new_data()

            # Check for status changes
            if old_data.get('status') != new_data.get('status'):
                logger.info(
                    f'Order status changed: {old_data.get("status")}'
                    f' -> {new_data.get("status")}'
                )
                # Example: Send status update email, trigger fulfillment

    def handle_product_change(self, handler: NotificationHandler):
        """Handle product table changes."""
        if handler.is_update():
            old_data = handler.get_old_data()
            new_data = handler.get_new_data()

            # Check for price changes
            if old_data.get('price') != new_data.get('price'):
                logger.info(
                    f'Product price changed: {old_data.get("price")}'
                    f' -> {new_data.get("price")}'
                )
                # Example: Update search index, notify price watchers

            # Check for inventory changes
            if old_data.get('stock_quantity') != new_data.get('stock_quantity'):
                old_qty = old_data.get('stock_quantity', 0)
                new_qty = new_data.get('stock_quantity', 0)

                if old_qty > 0 and new_qty == 0:
                    logger.warning(f'Product out of stock: {new_data.get("name")}')
                    # Example: Send out of stock notification
                elif old_qty == 0 and new_qty > 0:
                    logger.info(f'Product back in stock: {new_data.get("name")}')
                    # Example: Send back in stock notification

    def handle_generic_change(self, handler: NotificationHandler):
        """Handle changes for tables without specific handlers."""
        logger.info(
            f'Generic change on table {handler.get_table()}: {handler.get_action()}'
        )
        # Example: Log to analytics, update cache, etc.

    def stdout_write(self, message):
        """Output messages (can be overridden in subclasses)."""
        print(message)


class CacheInvalidationConsumer(BaseConsumer):
    """
    Example consumer that invalidates caches based on database changes.
    """

    # Define which tables should trigger cache invalidation
    CACHE_INVALIDATION_TABLES = {
        'users': ['user_profile_*', 'user_permissions_*'],
        'products': ['product_catalog', 'product_search_*'],
        'categories': ['category_tree', 'navigation_menu'],
        'settings': ['site_config'],
    }

    def handle_notification(self, handler: NotificationHandler):
        """Handle cache invalidation based on table changes."""
        table = handler.get_table()

        if table in self.CACHE_INVALIDATION_TABLES:
            cache_keys = self.CACHE_INVALIDATION_TABLES[table]
            record_id = handler.get_record_id()

            for cache_key in cache_keys:
                if '*' in cache_key:
                    # Wildcard cache key - include record ID
                    full_cache_key = cache_key.replace('*', str(record_id))
                else:
                    full_cache_key = cache_key

                self.invalidate_cache(full_cache_key)
                logger.info(f'Invalidated cache key: {full_cache_key}')

        # Always invalidate related object caches
        self.invalidate_related_caches(handler)

    def invalidate_cache(self, cache_key: str):
        """Invalidate a specific cache key."""
        # Example implementation - replace with your cache backend
        try:
            from django.core.cache import cache

            cache.delete(cache_key)
        except ImportError:
            logger.warning('Django cache not available for invalidation')

    def invalidate_related_caches(self, handler: NotificationHandler):
        """Invalidate caches related to the changed record."""
        table = handler.get_table()
        # Get record ID for cache key formatting below
        # record_id is used for forming cache keys in real implementations
        record_id = handler.get_record_id()

        # Example: Invalidate list views that might include this record
        list_cache_keys = [
            f'{table}_list_page_*',
            f'{table}_search_*',
            'homepage_data',
        ]

        for cache_key in list_cache_keys:
            if '*' in cache_key:
                # Real impl would find & delete all matching keys with the record ID
                # This is a simplified example that uses the record_id
                self.invalidate_cache(cache_key.replace('*', str(record_id)))
            else:
                self.invalidate_cache(cache_key)


class WebhookConsumer(BaseConsumer):
    """
    Example consumer that sends webhooks for specific events.
    """

    # Define webhook configurations
    WEBHOOK_CONFIGS = {
        'users': {
            'INSERT': 'user.created',
            'UPDATE': 'user.updated',
            'DELETE': 'user.deleted',
        },
        'orders': {
            'INSERT': 'order.created',
            'UPDATE': 'order.updated',
        },
    }

    def handle_notification(self, handler: NotificationHandler):
        """Send webhooks for configured table/action combinations."""
        table = handler.get_table()
        action = handler.get_action()

        if table in self.WEBHOOK_CONFIGS:
            webhook_configs = self.WEBHOOK_CONFIGS[table]

            if action in webhook_configs:
                event_type = webhook_configs[action]
                self.send_webhook(event_type, handler)

    def send_webhook(self, event_type: str, handler: NotificationHandler):
        """Send a webhook for the event."""
        webhook_data = {
            'event_type': event_type,
            'timestamp': handler.timestamp,
            'table': handler.get_table(),
            'action': handler.get_action(),
            'record_id': handler.get_record_id(),
            'data': {
                'old': handler.get_old_data(),
                'new': handler.get_new_data(),
            },
        }

        logger.info(f'Sending webhook: {event_type} for record {handler.get_record_id()}')

        # Example webhook sending (replace with your implementation)
        # self.send_webhook_http(webhook_data)

        # For now, just log the webhook data
        logger.debug(f'Webhook data: {webhook_data}')

    def send_webhook_http(self, webhook_data: Dict[str, Any]):
        """Send webhook via HTTP (implement based on your needs)."""
        import requests

        webhook_url = 'https://your-webhook-endpoint.com/webhook'

        try:
            response = requests.post(
                webhook_url,
                json=webhook_data,
                headers={'Content-Type': 'application/json'},
                timeout=30,
            )
            response.raise_for_status()
            logger.info(f'Webhook sent successfully: {response.status_code}')

        except requests.RequestException as e:
            logger.error(f'Failed to send webhook: {e}')
            raise  # Re-raise to mark notification as unprocessed


class AnalyticsConsumer(BaseConsumer):
    """
    Example consumer that sends events to analytics services.
    """

    def handle_notification(self, handler: NotificationHandler):
        """Send analytics events for database changes."""
        # Skip replay events for analytics (only track real-time changes)
        if handler.is_replay:
            return

        event_name = f'{handler.get_table()}.{handler.get_action().lower()}'

        analytics_data = {
            'event': event_name,
            'timestamp': handler.timestamp,
            'properties': {
                'table': handler.get_table(),
                'record_id': handler.get_record_id(),
                'consumer_id': self.consumer_id,
            },
        }

        # Add specific data based on action
        if handler.is_insert() or handler.is_update():
            new_data = handler.get_new_data()
            if new_data:
                # Add relevant fields (be careful about PII)
                analytics_data['properties'].update(
                    {
                        'created_at': new_data.get('created_at'),
                        'updated_at': new_data.get('updated_at'),
                    }
                )

        self.send_analytics_event(analytics_data)

    def send_analytics_event(self, event_data: Dict[str, Any]):
        """Send event to analytics service."""
        logger.info(f'Analytics event: {event_data["event"]}')

        # Example: Send to your analytics service
        # amplitude.track(event_data)
        # mixpanel.track(event_data)
        # segment.track(event_data)

        logger.debug(f'Analytics data: {event_data}')


# Example usage functions
def send_custom_notification(channel: str, event_type: str, data: Dict[str, Any]):
    """
    Helper function to send custom notifications.

    Example:
        send_custom_notification('user_events', 'login', {
            'user_id': 123,
            'ip_address': '192.168.1.1',
            'user_agent': 'Mozilla/5.0...'
        })
    """
    payload = {
        'event_type': event_type,
        'data': data,
        'timestamp': time.time(),
    }

    return smart_notify(channel, payload)


def create_trigger_for_table(table_name: str, channel: str = 'data_change'):
    """
    Helper function to create a notification trigger for a table.

    Example:
        create_trigger_for_table('users')
        create_trigger_for_table('orders', 'order_events')
    """
    from django.db import connection

    trigger_name = f'notify_{table_name}_changes'

    sql = f"""
    CREATE TRIGGER {trigger_name}
        AFTER INSERT OR UPDATE OR DELETE ON {table_name}
        FOR EACH ROW EXECUTE FUNCTION notify_data_change();
    """

    with connection.cursor() as cursor:
        cursor.execute(sql)

    return trigger_name
