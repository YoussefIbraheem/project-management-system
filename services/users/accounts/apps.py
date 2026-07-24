from django.apps import AppConfig
from django.core.signals import request_finished

class MyAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        from accounts.mailers.password_reset import send_password_reset_email # noqa
