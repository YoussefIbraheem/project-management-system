import logging
import os

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.forms import model_to_dict
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from accounts.models import User

logger = logging.getLogger(__name__)


class UserVerificationEmail:
    VERIFICATION_TEMPLATE = "email_templates/user_verification.html"

    def __init__(self, user: User, code: str) -> None:
        self.user = user
        self.code = code    

    def _build_verification_url(self) -> str:
        base_url = getattr(settings, "FRONTEND_VERIFICATION_URL", "")
        if not base_url:
            logger.warning(
                "FRONTEND_VERIFICATION_URL is not configured; verification link will be empty for user %s",
                self.user.id,
            )
            return ""
        return f"{base_url}?email={self.user.email}&code={self.code}"

    def send(self):
        try:
            context = {
                "user": self.user,
                "verification_code": self.code,
                "verification_url": self._build_verification_url(),
                "app_name": getattr(settings, "APP_NAME", "Our App"),
                "site_url": getattr(settings, "SITE_URL", ""),
            }

            try:
                html_content = render_to_string(self.VERIFICATION_TEMPLATE, context)
            except TemplateDoesNotExist:
                logger.exception(
                    "Verification email template not found: %s",
                    self.VERIFICATION_TEMPLATE,
                )
                return False

            text_content = strip_tags(html_content)

            email = EmailMultiAlternatives(
                subject="User Verification",
                to=[self.user.email],
                body=text_content,
            )

            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False) # TODO: Create a background work as it takes a long time to prcess (Celery)
            return True
        except Exception as e:
            print(f"Error sending verification email: {e}")
            return False
