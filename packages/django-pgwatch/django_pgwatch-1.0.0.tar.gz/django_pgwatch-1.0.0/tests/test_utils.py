import json
from unittest.mock import MagicMock, patch

import pytest
from django.test import TestCase

from django_pgwatch.models import NotificationLog
from django_pgwatch.utils import cleanup_old_notifications, smart_notify


class UtilsTest(TestCase):
    
    @patch('django_pgwatch.utils.connection')
    def test_smart_notify_basic(self, mock_connection):
        """Test basic smart_notify functionality"""
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        test_payload = {'action': 'INSERT', 'table': 'users', 'id': 123}
        
        notification_id = smart_notify('test_channel', test_payload)
        
        # Check that notification was created in database
        notification = NotificationLog.objects.get(id=notification_id)
        self.assertEqual(notification.channel, 'test_channel')
        self.assertEqual(notification.payload, test_payload)
        
        # Check that pg_notify was called
        mock_cursor.execute.assert_called_once()
        call_args = mock_cursor.execute.call_args
        self.assertEqual(call_args[0][0], 'SELECT pg_notify(%s, %s)')
        self.assertEqual(call_args[0][1][0], 'test_channel')
        
        # Check payload structure
        sent_payload = json.loads(call_args[0][1][1])
        self.assertEqual(sent_payload['notification_log_id'], notification_id)
        self.assertEqual(sent_payload['data'], test_payload)
        self.assertIn('timestamp', sent_payload)
        
    @patch('django_pgwatch.utils.connection')
    def test_smart_notify_no_payload(self, mock_connection):
        """Test smart_notify with no payload"""
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        notification_id = smart_notify('test_channel')
        
        # Check that notification was created with empty payload
        notification = NotificationLog.objects.get(id=notification_id)
        self.assertEqual(notification.channel, 'test_channel')
        self.assertEqual(notification.payload, {})
        
    @patch('django_pgwatch.utils.connection')
    def test_smart_notify_large_payload(self, mock_connection):
        """Test smart_notify with large payload"""
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        # Create a large payload (> 7500 bytes when JSON encoded)
        large_data = {'data': 'x' * 8000}
        
        notification_id = smart_notify('test_channel', large_data)
        
        # Check that notification was created with full payload
        notification = NotificationLog.objects.get(id=notification_id)
        self.assertEqual(notification.payload, large_data)
        
        # Check that minimal payload was sent via NOTIFY
        call_args = mock_cursor.execute.call_args
        sent_payload = json.loads(call_args[0][1][1])
        self.assertEqual(sent_payload['notification_log_id'], notification_id)
        self.assertTrue(sent_payload['large_payload'])
        self.assertNotIn('data', sent_payload)  # Large data should not be in NOTIFY
        
    @patch('django_pgwatch.models.NotificationLog.cleanup_old')
    def test_cleanup_old_notifications(self, mock_cleanup):
        """Test cleanup_old_notifications function"""
        mock_cleanup.return_value = 5
        
        # Test with default days
        result = cleanup_old_notifications()
        mock_cleanup.assert_called_with(7)
        self.assertEqual(result, 5)
        
        # Test with custom days
        result = cleanup_old_notifications(days_to_keep=14)
        mock_cleanup.assert_called_with(14)
        self.assertEqual(result, 5)
        
    def test_create_trigger_for_table_default_channel(self):
        """Test create_trigger_for_table with default channel"""
        from django_pgwatch.utils import create_trigger_for_table
        
        sql = create_trigger_for_table('users')
        
        expected_parts = [
            'CREATE TRIGGER notify_users_changes',
            'AFTER INSERT OR UPDATE OR DELETE ON users',
            'FOR EACH ROW EXECUTE FUNCTION notify_data_change()'
        ]
        
        for part in expected_parts:
            self.assertIn(part, sql)
            
    def test_create_trigger_for_table_custom_channel(self):
        """Test create_trigger_for_table with custom channel"""
        from django_pgwatch.utils import create_trigger_for_table
        
        sql = create_trigger_for_table('orders', 'order_changes')
        
        expected_parts = [
            'CREATE TRIGGER notify_orders_changes',
            'AFTER INSERT OR UPDATE OR DELETE ON orders',
            'FOR EACH ROW EXECUTE FUNCTION notify_data_change()'
        ]
        
        for part in expected_parts:
            self.assertIn(part, sql)