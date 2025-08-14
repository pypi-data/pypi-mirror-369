import json
import logging
import select
import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, List, Optional

import psycopg
from django.conf import settings
from django.db import connection

from .models import NotificationLog

logger = logging.getLogger(__name__)


class NotificationHandler:
    """
    Wrapper for PostgreSQL LISTEN/NOTIFY notification data and metadata.

    This class encapsulates notification data received from PostgreSQL's LISTEN/NOTIFY
    system, providing convenient access to notification metadata and specialized
    methods for handling database change notifications.

    Key Features:
    - Wraps raw notification payload with metadata (timestamp, channel, replay status)
    - Provides convenience methods for database change notifications (table, action,
      record data)
    - Tracks processing metadata (when processed, whether it's a replay)
    - Offers type checking methods (is_insert, is_update, is_delete)

    Args:
        notification_log_id: Unique ID from the notification log table
        data: The notification payload (typically database change data)
        channel: PostgreSQL channel name the notification was received on
        timestamp: When the notification was originally created
        is_replay: Whether this notification is being replayed (vs real-time)

    Example:
        >>> handler = NotificationHandler(
        ...     notification_log_id=123,
        ...     data={'table': 'users', 'action': 'INSERT', 'id': 456},
        ...     channel='data_change',
        ...     timestamp=1628123456.0,
        ...     is_replay=True
        ... )
        >>> handler.get_table()  # 'users'
        >>> handler.is_insert()  # True
    """

    def __init__(
        self,
        notification_log_id: int,
        data: Dict[str, Any],
        channel: str,
        timestamp: float,
        is_replay: bool = False,
    ):
        self.notification_log_id = notification_log_id
        self.data = data
        self.channel = channel
        self.timestamp = timestamp
        self.is_replay = is_replay
        self.processed_at = time.time()

    def __str__(self):
        replay_status = 'replay' if self.is_replay else 'real-time'
        return (
            f'Notification {self.notification_log_id} on {self.channel} ({replay_status})'
        )

    def get_table(self) -> Optional[str]:
        """Get table name if this is a database change notification."""
        return self.data.get('table')

    def get_action(self) -> Optional[str]:
        """Get action type if this is a database change notification."""
        return self.data.get('action')

    def get_record_id(self) -> Any:
        """Get record ID if this is a database change notification."""
        return self.data.get('id')

    def get_old_data(self) -> Optional[Dict]:
        """Get old record data for UPDATE/DELETE operations."""
        return self.data.get('old_data')

    def get_new_data(self) -> Optional[Dict]:
        """Get new record data for INSERT/UPDATE operations."""
        return self.data.get('new_data')

    def is_insert(self) -> bool:
        """Check if this is an INSERT operation."""
        return self.get_action() == 'INSERT'

    def is_update(self) -> bool:
        """Check if this is an UPDATE operation."""
        return self.get_action() == 'UPDATE'

    def is_delete(self) -> bool:
        """Check if this is a DELETE operation."""
        return self.get_action() == 'DELETE'


class BaseConsumer(ABC):
    """
    Base class for PostgreSQL LISTEN/NOTIFY consumers with playback capability.

    Provides:
    - Automatic playback of missed notifications
    - Real-time notification listening
    - Consumer progress tracking
    - Error handling and reconnection
    - Gap detection and recovery
    - Auto-discovery support via class attributes

    Class Attributes (for auto-discovery):
        consumer_id (str): Unique identifier for this consumer
        channels (List[str]): List of PostgreSQL channels to listen on
    """

    # Class attributes for auto-discovery (can be overridden by subclasses)
    consumer_id: Optional[str] = None
    channels: List[str] = ['data_change']

    def __init__(
        self,
        consumer_id: str = None,
        channels: List[str] = None,
        timeout_seconds: int = 30,
        reconnect_delay: int = 5,
        max_batch_size: int = 100,
        max_workers: int = 4,
    ):
        # Use class attributes if instance parameters not provided
        self.consumer_id = consumer_id or self.__class__.consumer_id
        self.channels = channels or self.__class__.channels or ['data_change']

        # Validate that we have required attributes
        if not self.consumer_id:
            raise ValueError(
                f'Consumer {self.__class__.__name__} must specify consumer_id either '
                'as class attribute or constructor parameter'
            )
        self.timeout_seconds = timeout_seconds
        self.reconnect_delay = reconnect_delay
        self.max_batch_size = max_batch_size
        self.max_workers = max_workers
        self.last_processed_ids = {}
        self.connection = None
        self.running = False

        # Initialize last processed IDs for each channel
        for channel in self.channels:
            self.last_processed_ids[channel] = NotificationLog.get_last_processed_id(
                self.consumer_id, channel
            )

    def get_database_connection(self):
        """Create a new database connection for listening."""
        db_settings = settings.DATABASES['default']

        conn = psycopg.connect(
            host=db_settings['HOST'],
            port=db_settings.get('PORT', 5432),
            dbname=db_settings['NAME'],
            user=db_settings['USER'],
            password=db_settings['PASSWORD'],
            autocommit=True,
        )
        return conn

    def mark_processed(self, notification_log_id: int, channel: str):
        """Mark a notification as processed by this consumer."""
        try:
            notification = NotificationLog.objects.get(
                id=notification_log_id, channel=channel
            )
            notification.add_processed_by(self.consumer_id)
            self.last_processed_ids[channel] = max(
                self.last_processed_ids[channel], notification_log_id
            )
        except NotificationLog.DoesNotExist:
            logger.warning(
                f'Notification {notification_log_id} not found for marking as processed'
            )

    def _create_notification_handler(
        self, notification: 'NotificationLog', is_replay: bool = True
    ) -> NotificationHandler:
        """Create a NotificationHandler from a NotificationLog instance."""
        return NotificationHandler(
            notification_log_id=notification.id,
            data=notification.payload,
            channel=notification.channel,
            timestamp=notification.created_at.timestamp(),
            is_replay=is_replay,
        )

    def _process_notifications_batch(
        self, notifications: List['NotificationLog'], channel: str
    ) -> int:
        """Process a batch of notifications and return count of successfully processed."""
        if not notifications:
            return 0

        logger.info(
            f'Processing {len(notifications)} notifications on channel "{channel}"'
        )

        processed_count = 0

        # Process in parallel for better performance
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all notifications for processing
            futures = []
            for notification in notifications:
                handler = self._create_notification_handler(notification, is_replay=True)
                future = executor.submit(self._process_notification_safe, handler)
                futures.append((future, notification.id, channel))

            # Collect results without stopping on first error
            for future, notification_log_id, channel in futures:
                try:
                    if future.result():  # If processing succeeded
                        self.mark_processed(notification_log_id, channel)
                        processed_count += 1
                except Exception as e:
                    logger.error(
                        f'Error processing notification {notification_log_id}: {e}'
                    )
                    # Continue processing other notifications instead of breaking

        return processed_count

    def playback_missed_notifications(self):
        """Process all notifications since last processed ID for each channel."""
        total_processed = 0

        for channel in self.channels:
            last_id = self.last_processed_ids[channel]
            notifications = NotificationLog.get_unprocessed_for_consumer(
                self.consumer_id, channel, last_id
            )[: self.max_batch_size]

            if notifications:
                logger.info(
                    f'Playing back {len(notifications)} missed notifications '
                    f'on channel "{channel}"'
                )

                # Process batch and accumulate count
                processed = self._process_notifications_batch(notifications, channel)
                total_processed += processed

        if total_processed > 0:
            logger.info(f'Playback completed: {total_processed} notifications processed')

    def _process_notification_safe(self, handler: NotificationHandler) -> bool:
        """Safely process a notification with error handling."""
        try:
            self.handle_notification(handler)
            return True
        except Exception as e:
            logger.error(
                f'Error processing notification {handler.notification_log_id}: {e}'
            )
            return False

    def listen_for_real_time(self):
        """Listen for real-time notifications."""
        self.connection = self.get_database_connection()

        with self.connection.cursor() as cursor:
            # Subscribe to all channels
            for channel in self.channels:
                cursor.execute(f'LISTEN {channel};')
                logger.info(f"Listening on channel '{channel}'")

            logger.info(
                f"Consumer '{self.consumer_id}' ready for real-time notifications"
            )

            while self.running:
                try:
                    # Wait for notifications with timeout
                    if select.select([self.connection], [], [], self.timeout_seconds) == (
                        [],
                        [],
                        [],
                    ):
                        # Timeout - check for any gaps in processing
                        self.check_for_gaps()
                        continue

                    # Process all available notifications
                    for notify in self.connection.notifies():
                        self.handle_real_time_notification(notify.channel, notify.payload)

                except KeyboardInterrupt:
                    logger.info('Received interrupt signal, shutting down...')
                    break
                except Exception as e:
                    logger.error(f'Listener error: {e}')
                    self.reconnect()

    def handle_real_time_notification(self, channel: str, payload_str: str):
        """Handle a real-time notification."""
        try:
            notification = json.loads(payload_str)
            notification_log_id = notification['notification_log_id']

            # Skip if already processed (duplicate or out-of-order)
            if notification_log_id <= self.last_processed_ids[channel]:
                logger.debug(
                    f'Skipping already processed notification {notification_log_id}'
                )
                return

            # Handle large payloads
            if notification.get('large_payload'):
                data = self.fetch_notification_data(notification_log_id)
                if not data:
                    logger.warning(
                        f'Could not fetch data for notification {notification_log_id}'
                    )
                    return
            else:
                data = notification['data']

            handler = NotificationHandler(
                notification_log_id=notification_log_id,
                data=data,
                channel=channel,
                timestamp=notification['timestamp'],
                is_replay=False,
            )

            if self._process_notification_safe(handler):
                self.mark_processed(notification_log_id, channel)

        except json.JSONDecodeError as e:
            logger.error(f'Invalid JSON in notification: {e}')
        except Exception as e:
            logger.error(f'Error handling real-time notification: {e}')

    def fetch_notification_data(self, notification_log_id: int) -> Optional[Dict]:
        """Fetch notification data from log table for large payloads."""
        try:
            notification = NotificationLog.objects.get(id=notification_log_id)
            return notification.payload
        except NotificationLog.DoesNotExist:
            return None

    def check_for_gaps(self, max_gap_notifications: int = 100):
        """Check for any gaps in processed notifications and fill them."""
        for channel in self.channels:
            missed_notifications = NotificationLog.get_unprocessed_for_consumer(
                self.consumer_id, channel, self.last_processed_ids[channel]
            )[:max_gap_notifications]

            if missed_notifications:
                logger.info(
                    f'Found {len(missed_notifications)} missed notifications '
                    f'on channel "{channel}"'
                )

                # Process missed notifications sequentially for gap filling
                for notification in missed_notifications:
                    handler = self._create_notification_handler(
                        notification, is_replay=True
                    )
                    if self._process_notification_safe(handler):
                        self.mark_processed(notification.id, channel)

    def reconnect(self):
        """Reconnect to the database after an error."""
        logger.info(f'Reconnecting in {self.reconnect_delay} seconds...')
        time.sleep(self.reconnect_delay)

        try:
            if self.connection:
                self.connection.close()
        except Exception:
            pass

        try:
            self.connection = self.get_database_connection()
            logger.info('Reconnected successfully')
        except Exception as e:
            logger.error(f'Reconnection failed: {e}')

    def start(self):
        """Start the consumer with playback and real-time listening."""
        logger.info(
            f"Starting consumer '{self.consumer_id}' on channels: {self.channels}"
        )

        for channel in self.channels:
            logger.info(
                f"Last processed ID for channel '{channel}':"
                f' {self.last_processed_ids[channel]}'
            )

        # First, catch up on missed notifications
        self.playback_missed_notifications()

        # Then listen for real-time notifications
        self.running = True
        self.listen_for_real_time()

    def stop(self):
        """Stop the consumer gracefully."""
        logger.info(f"Stopping consumer '{self.consumer_id}'")
        self.running = False

        if self.connection:
            try:
                self.connection.close()
            except Exception:
                pass

    @abstractmethod
    def handle_notification(self, handler: NotificationHandler):
        """
        Handle a notification. Must be implemented by subclasses.

        Args:
            handler (NotificationHandler): The notification to process

        Raises:
            Exception: If processing fails (will be logged and notification
                won't be marked as processed)
        """
        pass
