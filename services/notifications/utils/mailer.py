from datetime import datetime, timezone
from email.message import EmailMessage
import aiosmtplib
from app import rmq_logger
from app.core.config import settings
from app.models.email_log import EmailStatus
from app.services.email_log_service import create_email_log, update_email_log
from app.templates import NotificationContent
from stamina import retry_context
from .email_validator import validate_email , EmailValidationError





class EmailService:
    def __init__(self, settings, logger, smtp_client_factory=aiosmtplib.SMTP):
        self.settings = settings
        self.logger = logger
        self.smtp_client_factory = smtp_client_factory

    async def send_email(self, content: NotificationContent):
        self.logger.info("Sending email...")

        try:
            recipient = await validate_email(content.recipient_email)
        except EmailValidationError as e:
            self.logger.error(
                "Refusing to send — invalid recipient %s: %s",
                content.recipient_email,
                e,
            )
            return False

        message = EmailMessage()
        message["From"] = self.settings.SMTP_USERNAME
        message["To"] = content.recipient_email
        message["Subject"] = content.subject
        message.set_content(content.body)

        smtp_params = {
            "hostname": self.settings.SMTP_HOSTNAME,
            "port": self.settings.SMTP_PORT,
            "use_tls": self.settings.SMTP_USE_TLS,
            "start_tls": self.settings.SMTP_START_TLS,
            "username": self.settings.SMTP_USERNAME,
            "password": self.settings.SMTP_PASSWORD,
        }

        email_log = None

        async for attempt in retry_context(
            on=aiosmtplib.SMTPException, attempts=self.settings.SMTP_MAX_ATTEMPTS
        ):
            with attempt:
                smtp_client = self.smtp_client_factory(**smtp_params)
                try:
                    # INFO: Connect SMTP
                    await smtp_client.connect()
                    rmq_logger.info("Connected to SMTP server...")

                    if content.notification_id:
                        if attempt.num == 1:  # INFO: the original attempt
                            email_log = create_email_log(
                                notification_id=content.notification_id,
                                email_address=self.settings.SMTP_USERNAME,
                                recipient_email=recipient,
                                attempts=attempt.num,
                            )
                        else:  # INFO: attempt.num > 1
                            update_email_log(
                                email_log_id=email_log.id,
                                status=EmailStatus.RETRYING.value,
                                attempts=attempt.num,
                            )

                    # INFO: Send Mail
                    await smtp_client.send_message(message)
                    self.logger.info("Message sent...")

                    if email_log is not None:
                        update_email_log(
                            email_log_id=email_log.id,
                            status=EmailStatus.SENT.value,
                            attempts=attempt.num,
                            sent_at=datetime.now(
                                timezone.utc
                            ),  # NOTE: The time of which the email was sent successfully, not when the log created
                        )

                    self.logger.info("Email sent successfully!")
                    return True

                except aiosmtplib.SMTPException as e:
                    self.logger.error(
                        f"Attempt {attempt.num} failed due to SMTPException: {e}"
                    )

                    if attempt.num >= settings.SMTP_MAX_ATTEMPTS: # INFO: Exceeded all attempts (Fail Scenario)
                        if email_log is not None:
                            update_email_log(
                                email_log_id=email_log.id,
                                status=EmailStatus.FAILED.value,
                                attempts=attempt.num,
                                error_message=str(e),
                            )
                            return False
                    raise
                finally:
                    try:
                        if smtp_client.is_connected:
                            await smtp_client.quit()
                    except Exception:
                        pass
