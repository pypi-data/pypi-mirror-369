from django.core.management.base import BaseCommand
from django.utils import timezone

from django_pgwatch.utils import cleanup_old_notifications


class Command(BaseCommand):
    help = 'Clean up old notification logs to prevent table bloat'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days to keep notifications (default: 7)',
        )

        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']

        if dry_run:
            from django_pgwatch.models import NotificationLog

            cutoff_date = timezone.now() - timezone.timedelta(days=days)
            count = NotificationLog.objects.filter(created_at__lt=cutoff_date).count()

            self.stdout.write(
                f'DRY RUN: Would delete {count} notification logs older than {days} days '
                f'(before {cutoff_date.strftime("%Y-%m-%d %H:%M:%S")})'
            )
        else:
            deleted_count = cleanup_old_notifications(days)

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully deleted {deleted_count} notification logs '
                    f'older than {days} days'
                )
            )
