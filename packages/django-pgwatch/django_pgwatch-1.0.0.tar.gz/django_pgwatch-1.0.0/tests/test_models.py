import json
from datetime import timedelta

import pytest
from django.test import TestCase
from django.utils import timezone

from django_pgwatch.models import NotificationLog


class NotificationLogTest(TestCase):
    def setUp(self):
        self.test_payload = {'action': 'INSERT', 'table': 'users', 'id': 123}
        
    def test_create_notification(self):
        """Test creating a notification log entry"""
        notification = NotificationLog.objects.create(
            channel='test_channel',
            payload=self.test_payload
        )
        
        self.assertEqual(notification.channel, 'test_channel')
        self.assertEqual(notification.payload, self.test_payload)
        self.assertEqual(len(notification.processed_by), 0)
        self.assertIsNotNone(notification.created_at)
        
    def test_add_processed_by(self):
        """Test adding a consumer to processed list"""
        notification = NotificationLog.objects.create(
            channel='test_channel',
            payload=self.test_payload
        )
        
        # Add first consumer
        notification.add_processed_by('consumer_1')
        self.assertIn('consumer_1', notification.processed_by)
        
        # Add second consumer
        notification.add_processed_by('consumer_2')
        self.assertIn('consumer_1', notification.processed_by)
        self.assertIn('consumer_2', notification.processed_by)
        
        # Try to add same consumer again (should not duplicate)
        notification.add_processed_by('consumer_1')
        self.assertEqual(notification.processed_by.count('consumer_1'), 1)
        
    def test_is_processed_by(self):
        """Test checking if notification was processed by consumer"""
        notification = NotificationLog.objects.create(
            channel='test_channel',
            payload=self.test_payload
        )
        
        self.assertFalse(notification.is_processed_by('consumer_1'))
        
        notification.add_processed_by('consumer_1')
        self.assertTrue(notification.is_processed_by('consumer_1'))
        self.assertFalse(notification.is_processed_by('consumer_2'))
        
    def test_payload_size(self):
        """Test payload size calculation"""
        small_payload = {'id': 1}
        large_payload = {'data': 'x' * 1000}
        
        small_notification = NotificationLog.objects.create(
            channel='test',
            payload=small_payload
        )
        large_notification = NotificationLog.objects.create(
            channel='test',
            payload=large_payload
        )
        
        self.assertLess(small_notification.payload_size, large_notification.payload_size)
        self.assertEqual(
            small_notification.payload_size,
            len(json.dumps(small_payload).encode('utf-8'))
        )
        
    def test_get_unprocessed_for_consumer(self):
        """Test getting unprocessed notifications for a consumer"""
        # Create notifications
        n1 = NotificationLog.objects.create(channel='test', payload={'id': 1})
        n2 = NotificationLog.objects.create(channel='test', payload={'id': 2})
        n3 = NotificationLog.objects.create(channel='test', payload={'id': 3})
        
        # Mark n1 as processed by consumer_1
        n1.add_processed_by('consumer_1')
        
        # Get unprocessed for consumer_1
        unprocessed = NotificationLog.get_unprocessed_for_consumer('consumer_1')
        unprocessed_ids = list(unprocessed.values_list('id', flat=True))
        
        self.assertNotIn(n1.id, unprocessed_ids)
        self.assertIn(n2.id, unprocessed_ids)
        self.assertIn(n3.id, unprocessed_ids)
        
        # Get unprocessed for consumer_2 (should get all)
        unprocessed = NotificationLog.get_unprocessed_for_consumer('consumer_2')
        unprocessed_ids = list(unprocessed.values_list('id', flat=True))
        
        self.assertIn(n1.id, unprocessed_ids)
        self.assertIn(n2.id, unprocessed_ids)
        self.assertIn(n3.id, unprocessed_ids)
        
    def test_get_unprocessed_with_channel_filter(self):
        """Test getting unprocessed notifications filtered by channel"""
        # Create notifications on different channels
        n1 = NotificationLog.objects.create(channel='channel_1', payload={'id': 1})
        n2 = NotificationLog.objects.create(channel='channel_2', payload={'id': 2})
        
        # Get unprocessed for specific channel
        unprocessed = NotificationLog.get_unprocessed_for_consumer(
            'consumer_1', 
            channel='channel_1'
        )
        unprocessed_ids = list(unprocessed.values_list('id', flat=True))
        
        self.assertIn(n1.id, unprocessed_ids)
        self.assertNotIn(n2.id, unprocessed_ids)
        
    def test_get_last_processed_id(self):
        """Test getting the last processed notification ID"""
        # Create notifications
        n1 = NotificationLog.objects.create(channel='test', payload={'id': 1})
        n2 = NotificationLog.objects.create(channel='test', payload={'id': 2})
        n3 = NotificationLog.objects.create(channel='test', payload={'id': 3})
        
        # Initially no processed notifications
        last_id = NotificationLog.get_last_processed_id('consumer_1', 'test')
        self.assertEqual(last_id, 0)
        
        # Mark n1 and n3 as processed
        n1.add_processed_by('consumer_1')
        n3.add_processed_by('consumer_1')
        
        # Should get the highest ID
        last_id = NotificationLog.get_last_processed_id('consumer_1', 'test')
        self.assertEqual(last_id, n3.id)
        
    def test_cleanup_old(self):
        """Test cleaning up old notifications"""
        old_time = timezone.now() - timedelta(days=10)
        recent_time = timezone.now() - timedelta(hours=1)
        
        # Create old and recent notifications
        old_notification = NotificationLog.objects.create(
            channel='test',
            payload={'id': 1}
        )
        recent_notification = NotificationLog.objects.create(
            channel='test',
            payload={'id': 2}
        )
        
        # Manually set created_at times
        NotificationLog.objects.filter(id=old_notification.id).update(
            created_at=old_time
        )
        NotificationLog.objects.filter(id=recent_notification.id).update(
            created_at=recent_time
        )
        
        # Clean up notifications older than 7 days
        deleted_count = NotificationLog.cleanup_old(days_to_keep=7)
        
        self.assertEqual(deleted_count, 1)
        self.assertFalse(
            NotificationLog.objects.filter(id=old_notification.id).exists()
        )
        self.assertTrue(
            NotificationLog.objects.filter(id=recent_notification.id).exists()
        )
        
    def test_string_representation(self):
        """Test string representation of NotificationLog"""
        notification = NotificationLog.objects.create(
            channel='test_channel',
            payload=self.test_payload
        )
        
        expected_str = f'Notification {notification.id} on test_channel'
        self.assertEqual(str(notification), expected_str)