from celery import shared_task
from django.conf import settings

from accounts.models import User

from . import get_task_logger, logger, send_email

task_logger = get_task_logger(__name__)

_VERIFICATION_TEMPLATE = "email_templates/user_verification.html"


def _build_verification_url(user, code) -> str:
    base_url = getattr(settings, "FRONTEND_VERIFICATION_URL", "")
    if not base_url:
        logger.warning(
            "FRONTEND_VERIFICATION_URL is not configured; verification link will be empty for user %s",
            user.id,
        )
        return ""
    return f"{base_url}?email={user.email}&code={code}"


@shared_task
def send_verification_email(user_id: int, code: str):
    try:
        user = User.objects.get(id=user_id)

        context = {
            "user": user,
            "verification_code": code,
            "verification_url": _build_verification_url(user, code),
            "app_name": getattr(settings, "APP_NAME", "Our App"),
            "site_url": getattr(settings, "SITE_URL", ""),
        }
        task_logger.info("Sending verification email to %s", user.email)
        return send_email(_VERIFICATION_TEMPLATE, context, user.email)

    except Exception as e:
        print(f"Error sending verification email: {e}")
        return False
