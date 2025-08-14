from django.apps import AppConfig


class DjangoPgwatchConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_pgwatch'
    verbose_name = 'PostgreSQL Watch'
