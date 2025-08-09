from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tailorNow.accounts'

    def ready(self):
        # Import signals to ensure they are registered
        from . import signals  # noqa: F401
