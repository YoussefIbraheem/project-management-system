from celery import shared_task
from django.conf import settings
from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created

from . import send_email

_PASSWORD_RESET_TEMPLATE = "email_templates/password_reset.html"


def _build_password_reset_token_url(instance, reset_password_token):
    return "{}?token={}".format(
        instance.request.build_absolute_uri(
            reverse("password_reset:reset-password-confirm")
        ),
        reset_password_token.key,
    )


@shared_task
def _dispatch_password_reset_email(user_id: int, reset_url: str):
    from accounts.models import (
        User,
    )

    user = User.objects.get(id=user_id)
    context = {
        "user": user,
        "app_name": getattr(settings, "APP_NAME", "Our App"),
        "site_url": getattr(settings, "SITE_URL", ""),
        "reset_url": reset_url,
    }
    send_email(_PASSWORD_RESET_TEMPLATE, context, user.email,"Password Reset")


@receiver(reset_password_token_created)
def send_password_reset_email(sender, instance, reset_password_token, *args, **kwargs):
    try:
        reset_url = _build_password_reset_token_url(instance, reset_password_token)
        _dispatch_password_reset_email.delay(reset_password_token.user.id, reset_url)
    except Exception as e:
        print("Error sending password reset email:", str(e))
        raise
