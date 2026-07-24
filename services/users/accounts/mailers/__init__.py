import logging
from celery.utils.log import get_task_logger 

from django.core.mail import EmailMultiAlternatives
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

def send_email(template, context, email):
    try:
        html_content = render_to_string(template, context)
    except TemplateDoesNotExist:
        logger.exception(
            "Verification email template not found: %s",
            template,
        )
        return False

    text_content = strip_tags(html_content)

    email_content = EmailMultiAlternatives(
        subject="User Verification",
        to=[email],
        body=text_content,
    )

    email_content.attach_alternative(html_content, "text/html")
    email_content.send(fail_silently=False)
    logger.info("Verification Email sent to %s", email)
    return True
