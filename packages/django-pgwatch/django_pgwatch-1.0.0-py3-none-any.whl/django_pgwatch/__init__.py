"""
Django PostgreSQL LISTEN/NOTIFY with persistence and playback capabilities.
"""

__version__ = '1.0.0'
__author__ = 'Ed Menendez'
__email__ = 'ed@edmenendez.com'

# Import utilities directly when needed to avoid model import issues:
# from django_pgwatch.utils import smart_notify, cleanup_old_notifications
# from django_pgwatch.consumer import BaseConsumer, NotificationHandler
# from django_pgwatch.models import NotificationLog

__all__ = [
    '__version__',
    '__author__',
    '__email__',
]
