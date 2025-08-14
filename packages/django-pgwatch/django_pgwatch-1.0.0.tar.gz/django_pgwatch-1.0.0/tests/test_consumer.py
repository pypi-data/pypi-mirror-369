from unittest.mock import MagicMock, patch

import pytest
from django.test import TestCase

from django_pgwatch.consumer import BaseConsumer, NotificationHandler
from django_pgwatch.models import NotificationLog


class NotificationHandlerTest(TestCase):
    def test_notification_handler_basic(self):
        """Test basic NotificationHandler functionality"""
        data = {
            'table': 'users',
            'action': 'INSERT',
            'id': 123,
            'new_data': {'name': 'John', 'email': 'john@example.com'}
        }
        
        handler = NotificationHandler(
            notification_log_id=456,
            data=data,
            channel='data_change',
            timestamp=1234567890.0,
            is_replay=True
        )
        
        self.assertEqual(handler.notification_log_id, 456)
        self.assertEqual(handler.data, data)
        self.assertEqual(handler.channel, 'data_change')
        self.assertEqual(handler.timestamp, 1234567890.0)
        self.assertTrue(handler.is_replay)
        
    def test_notification_handler_database_methods(self):
        """Test database-specific methods of NotificationHandler"""
        data = {
            'table': 'users',
            'action': 'UPDATE',
            'id': 123,
            'old_data': {'name': 'John', 'email': 'john@example.com'},
            'new_data': {'name': 'John', 'email': 'john@newemail.com'}
        }
        
        handler = NotificationHandler(1, data, 'data_change', 0.0)
        
        self.assertEqual(handler.get_table(), 'users')
        self.assertEqual(handler.get_action(), 'UPDATE')
        self.assertEqual(handler.get_record_id(), 123)
        self.assertEqual(handler.get_old_data(), data['old_data'])
        self.assertEqual(handler.get_new_data(), data['new_data'])
        
        self.assertFalse(handler.is_insert())
        self.assertTrue(handler.is_update())
        self.assertFalse(handler.is_delete())
        
    def test_notification_handler_action_checks(self):
        """Test action type checking methods"""
        insert_handler = NotificationHandler(
            1, {'action': 'INSERT'}, 'test', 0.0
        )
        update_handler = NotificationHandler(
            2, {'action': 'UPDATE'}, 'test', 0.0
        )
        delete_handler = NotificationHandler(
            3, {'action': 'DELETE'}, 'test', 0.0
        )
        
        # INSERT checks
        self.assertTrue(insert_handler.is_insert())
        self.assertFalse(insert_handler.is_update())
        self.assertFalse(insert_handler.is_delete())
        
        # UPDATE checks
        self.assertFalse(update_handler.is_insert())
        self.assertTrue(update_handler.is_update())
        self.assertFalse(update_handler.is_delete())
        
        # DELETE checks
        self.assertFalse(delete_handler.is_insert())
        self.assertFalse(delete_handler.is_update())
        self.assertTrue(delete_handler.is_delete())
        
    def test_notification_handler_string_representation(self):
        """Test string representation of NotificationHandler"""
        handler = NotificationHandler(123, {}, 'test_channel', 0.0, is_replay=True)
        expected = 'Notification 123 on test_channel (replay)'
        self.assertEqual(str(handler), expected)
        
        handler = NotificationHandler(456, {}, 'live_channel', 0.0, is_replay=False)
        expected = 'Notification 456 on live_channel (real-time)'
        self.assertEqual(str(handler), expected)


class TestConsumer(BaseConsumer):
    """Test consumer for testing purposes"""
    consumer_id = 'test_consumer'
    channels = ['test_channel']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.handled_notifications = []
        
    def handle_notification(self, handler):
        self.handled_notifications.append(handler)


class BaseConsumerTest(TestCase):
    def test_consumer_initialization_with_class_attributes(self):
        """Test consumer initialization using class attributes"""
        consumer = TestConsumer()
        
        self.assertEqual(consumer.consumer_id, 'test_consumer')
        self.assertEqual(consumer.channels, ['test_channel'])
        
    def test_consumer_initialization_with_parameters(self):
        """Test consumer initialization with constructor parameters"""
        consumer = TestConsumer(
            consumer_id='custom_consumer',
            channels=['custom_channel_1', 'custom_channel_2']
        )
        
        self.assertEqual(consumer.consumer_id, 'custom_consumer')
        self.assertEqual(consumer.channels, ['custom_channel_1', 'custom_channel_2'])
        
    def test_consumer_requires_consumer_id(self):
        """Test that consumer requires consumer_id"""
        class InvalidConsumer(BaseConsumer):
            # Missing consumer_id
            channels = ['test']
            
            def handle_notification(self, handler):
                pass
                
        with self.assertRaises(ValueError) as cm:
            InvalidConsumer()
            
        self.assertIn('must specify consumer_id', str(cm.exception))
        
    def test_consumer_default_channels(self):
        """Test consumer with default channels"""
        class DefaultChannelConsumer(BaseConsumer):
            consumer_id = 'test'
            # No channels specified - should use default
            
            def handle_notification(self, handler):
                pass
                
        consumer = DefaultChannelConsumer()
        self.assertEqual(consumer.channels, ['data_change'])
        
    @patch('django_pgwatch.models.NotificationLog.get_last_processed_id')
    def test_consumer_initialization_loads_last_processed_ids(self, mock_get_last_id):
        """Test that consumer loads last processed IDs on initialization"""
        mock_get_last_id.side_effect = lambda consumer_id, channel: {
            ('test_consumer', 'test_channel'): 42
        }.get((consumer_id, channel), 0)
        
        consumer = TestConsumer()
        
        mock_get_last_id.assert_called_with('test_consumer', 'test_channel')
        self.assertEqual(consumer.last_processed_ids['test_channel'], 42)
        
    def test_mark_processed(self):
        """Test marking a notification as processed"""
        # Create a test notification
        notification = NotificationLog.objects.create(
            channel='test_channel',
            payload={'test': 'data'}
        )
        
        consumer = TestConsumer()
        consumer.mark_processed(notification.id, 'test_channel')
        
        # Reload from database
        notification.refresh_from_db()
        self.assertIn('test_consumer', notification.processed_by)
        self.assertEqual(consumer.last_processed_ids['test_channel'], notification.id)
        
    def test_create_notification_handler(self):
        """Test creating a NotificationHandler from NotificationLog"""
        notification = NotificationLog.objects.create(
            channel='test_channel',
            payload={'action': 'INSERT', 'table': 'users'}
        )
        
        consumer = TestConsumer()
        handler = consumer._create_notification_handler(notification, is_replay=True)
        
        self.assertEqual(handler.notification_log_id, notification.id)
        self.assertEqual(handler.data, notification.payload)
        self.assertEqual(handler.channel, 'test_channel')
        self.assertTrue(handler.is_replay)
        
    @patch('django_pgwatch.models.NotificationLog.get_unprocessed_for_consumer')
    def test_playback_missed_notifications_empty(self, mock_get_unprocessed):
        """Test playback when there are no missed notifications"""
        mock_get_unprocessed.return_value = NotificationLog.objects.none()
        
        consumer = TestConsumer()
        consumer.playback_missed_notifications()
        
        self.assertEqual(len(consumer.handled_notifications), 0)
        
    def test_process_notification_safe_success(self):
        """Test safe notification processing on success"""
        handler = NotificationHandler(1, {'test': 'data'}, 'test', 0.0)
        consumer = TestConsumer()
        
        result = consumer._process_notification_safe(handler)
        
        self.assertTrue(result)
        self.assertEqual(len(consumer.handled_notifications), 1)
        self.assertEqual(consumer.handled_notifications[0], handler)
        
    def test_process_notification_safe_exception(self):
        """Test safe notification processing on exception"""
        class FailingConsumer(BaseConsumer):
            consumer_id = 'failing_consumer'
            channels = ['test']
            
            def handle_notification(self, handler):
                raise Exception("Test exception")
        
        handler = NotificationHandler(1, {'test': 'data'}, 'test', 0.0)
        consumer = FailingConsumer()
        
        with patch('django_pgwatch.consumer.logger') as mock_logger:
            result = consumer._process_notification_safe(handler)
            
        self.assertFalse(result)
        mock_logger.error.assert_called_once()
        
    def test_fetch_notification_data_exists(self):
        """Test fetching notification data when it exists"""
        notification = NotificationLog.objects.create(
            channel='test',
            payload={'test': 'data'}
        )
        
        consumer = TestConsumer()
        data = consumer.fetch_notification_data(notification.id)
        
        self.assertEqual(data, {'test': 'data'})
        
    def test_fetch_notification_data_missing(self):
        """Test fetching notification data when it doesn't exist"""
        consumer = TestConsumer()
        data = consumer.fetch_notification_data(999999)  # Non-existent ID
        
        self.assertIsNone(data)