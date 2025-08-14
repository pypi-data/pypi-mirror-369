import importlib
import signal
import sys
from typing import List, Type

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError

from django_pgwatch.consumer import BaseConsumer


class Command(BaseCommand):
    help = 'Listen for PostgreSQL notifications with playback capability'

    def add_arguments(self, parser):
        parser.add_argument(
            '--apps',
            nargs='+',
            help='Only discover consumers from specific apps',
        )

        parser.add_argument(
            '--consumers',
            nargs='+',
            help='Only run specific consumers by consumer_id',
        )

        parser.add_argument(
            '--exclude-consumers',
            nargs='+',
            help='Exclude specific consumers by consumer_id',
        )

        # Common options
        parser.add_argument(
            '--timeout',
            type=int,
            default=30,
            help='Timeout in seconds for listening (default: 30)',
        )

        parser.add_argument(
            '--reconnect-delay',
            type=int,
            default=5,
            help='Delay in seconds before reconnecting after error (default: 5)',
        )

        parser.add_argument(
            '--max-batch-size',
            type=int,
            default=100,
            help='Maximum number of notifications to process in playback batch '
            '(default: 100)',
        )

        parser.add_argument(
            '--skip-playback',
            action='store_true',
            help='Skip playback of missed notifications and only listen for new ones',
        )

        parser.add_argument(
            '--list-consumers',
            action='store_true',
            help='List all discovered consumers and exit',
        )

    def handle(self, *args, **options):
        # Extract common options
        timeout = options['timeout']
        reconnect_delay = options['reconnect_delay']
        max_batch_size = options['max_batch_size']
        skip_playback = options['skip_playback']

        # Handle list consumers option
        if options['list_consumers']:
            self.list_consumers(
                app_names=options.get('apps'),
                consumer_ids=options.get('consumers'),
                exclude_consumer_ids=options.get('exclude_consumers'),
            )
            return

        # Auto-discover consumers
        consumers = self.discover_consumers(
            app_names=options.get('apps'),
            consumer_ids=options.get('consumers'),
            exclude_consumer_ids=options.get('exclude_consumers'),
        )

        if not consumers:
            raise CommandError(
                'No consumers found. Make sure you have consumers.py files in your apps.'
            )

        self.run_multiple_consumers(
            consumers, timeout, reconnect_delay, max_batch_size, skip_playback
        )

    def discover_consumers(
        self,
        app_names: List[str] = None,
        consumer_ids: List[str] = None,
        exclude_consumer_ids: List[str] = None,
    ) -> List[Type[BaseConsumer]]:
        """Discover consumers from INSTALLED_APPS."""
        discovered_consumers = []
        exclude_consumer_ids = exclude_consumer_ids or []

        # Get list of apps to search
        if app_names:
            app_configs = []
            for name in app_names:
                try:
                    app_configs.append(apps.get_app_config(name))
                except LookupError:
                    self.stdout.write(
                        self.style.WARNING(f'App "{name}" not found in INSTALLED_APPS')
                    )
        else:
            app_configs = apps.get_app_configs()

        for app_config in app_configs:
            try:
                # Try to import consumers.py from each app
                consumers_module_path = f'{app_config.name}.consumers'
                consumers_module = importlib.import_module(consumers_module_path)

                # Find all BaseConsumer subclasses
                for name in dir(consumers_module):
                    obj = getattr(consumers_module, name)
                    if (
                        isinstance(obj, type)
                        and issubclass(obj, BaseConsumer)
                        and obj != BaseConsumer
                    ):
                        # Check if consumer has required attributes
                        if not obj.consumer_id:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'Skipping {obj.__name__} in {app_config.name}: '
                                    'no consumer_id defined'
                                )
                            )
                            continue

                        # Apply filters
                        if consumer_ids and obj.consumer_id not in consumer_ids:
                            continue

                        if obj.consumer_id in exclude_consumer_ids:
                            continue

                        discovered_consumers.append(obj)
                        self.stdout.write(
                            f'Discovered consumer: {obj.consumer_id} '
                            f'({obj.__name__} in {app_config.name})'
                        )

            except ImportError:
                # No consumers.py in this app - that's OK
                continue
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(
                        f'Error importing consumers from {app_config.name}: {e}'
                    )
                )

        return discovered_consumers

    def list_consumers(
        self,
        app_names: List[str] = None,
        consumer_ids: List[str] = None,
        exclude_consumer_ids: List[str] = None,
    ):
        """List all discoverable consumers."""
        consumers = self.discover_consumers(
            app_names=app_names,
            consumer_ids=consumer_ids,
            exclude_consumer_ids=exclude_consumer_ids,
        )

        if not consumers:
            self.stdout.write('No consumers found.')
            return

        self.stdout.write(f'\nFound {len(consumers)} consumer(s):\n')

        for consumer_class in consumers:
            app_name = consumer_class.__module__.split('.')[0]
            self.stdout.write(
                f'  • {consumer_class.consumer_id} '
                f'({consumer_class.__name__} in {app_name})'
            )
            self.stdout.write(f'    Channels: {consumer_class.channels}')
            self.stdout.write('')

    def run_multiple_consumers(
        self,
        consumer_classes: List[Type[BaseConsumer]],
        timeout: int,
        reconnect_delay: int,
        max_batch_size: int,
        skip_playback: bool,
    ):
        """Run multiple consumers in parallel (simplified single-process version)."""
        # For now, we'll run them sequentially in a single process
        # In the future, this could be enhanced to run in separate threads/processes

        if len(consumer_classes) > 1:
            self.stdout.write(
                self.style.WARNING(
                    f'Running {len(consumer_classes)} consumers sequentially in single '
                    'process. For parallel execution, run each consumer separately.'
                )
            )

        # For simplicity, just run the first consumer for now
        # TODO: Implement proper multi-consumer support
        consumer_class = consumer_classes[0]

        consumer = consumer_class(
            timeout_seconds=timeout,
            reconnect_delay=reconnect_delay,
            max_batch_size=max_batch_size,
        )

        self.run_consumer(consumer, skip_playback)

    def run_consumer(self, consumer: BaseConsumer, skip_playback: bool):
        """Run a single consumer with proper signal handling."""

        # Set up signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            self.stdout.write(f'Received signal {signum}, shutting down gracefully...')
            consumer.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Start the consumer
        self.stdout.write(
            self.style.SUCCESS(
                f"Starting consumer '{consumer.consumer_id}' "
                f'on channels: {consumer.channels}'
            )
        )

        if skip_playback:
            self.stdout.write(
                self.style.WARNING('Skipping playback of missed notifications')
            )
            consumer.running = True
            consumer.listen_for_real_time()
        else:
            consumer.start()
