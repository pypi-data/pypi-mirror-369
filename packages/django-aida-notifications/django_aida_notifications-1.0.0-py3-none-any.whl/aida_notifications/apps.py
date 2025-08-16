from django.apps import AppConfig


class AidaNotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aida_notifications'
    verbose_name = 'AIDA Notifications'

    def ready(self):
        try:
            import aida_notifications.signals
        except ImportError:
            pass
