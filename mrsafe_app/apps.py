from django.apps import AppConfig

class MrsafeAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mrsafe_app'

    def ready(self):
        import mrsafe_app.signals  # Ensure signals are connected
