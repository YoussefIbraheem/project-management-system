from email.message import EmailMessage
from stamina import retry_context
from app.core.config import settings
from app.templates import NotificationContent
from email_validator import validate_email as _validate_syntax, EmailNotValidError
import logging
import aiosmtplib
import dns.asyncresolver
import dns.resolver
from app import rmq_logger


class EmailValidationError(Exception):
    pass


async def _resolve_mx_hosts(domain: str) -> list[str]:
    resolver = dns.asyncresolver.Resolver()
    resolver.timeout = settings.DNS_TIMEOUT
    resolver.lifetime = settings.DNS_TIMEOUT
    try:
        answers = await resolver.resolve(domain, "MX")
        return [
            str(r.exchange).rstrip(".")
            for r in sorted(answers, key=lambda r: r.preference)
        ]
    except dns.resolver.NoAnswer:
        try:
            await resolver.resolve(domain, "A")
            return [domain]
        except Exception:
            return []
    except dns.resolver.NXDOMAIN:
        raise EmailValidationError(f"Domain does not exist: {domain}")
    except Exception as e:
        raise EmailValidationError(f"DNS lookup failed for {domain}: {e}")


async def validate_email(target_email: str) -> str:
    try:
        result = _validate_syntax(target_email, check_deliverability=False)
        normalized_email = result.normalized
        domain = result.domain.lower()
    except EmailNotValidError as e:
        raise EmailValidationError(f"Bad syntax: {e}")

    mx_hosts = await _resolve_mx_hosts(domain)
    if not mx_hosts:
        raise EmailValidationError(f"Domain has no mail servers configured: {domain}")

    last_error = None
    for host in mx_hosts:
        verify_client = aiosmtplib.SMTP(
            hostname=host, port=25, timeout=settings.SMTP_VERIFY_TIMEOUT
        )
        try:
            await verify_client.connect()
            await verify_client.helo()
            await verify_client.mail(settings.SMTP_USERNAME)
            code, message = await verify_client.rcpt(normalized_email)

            if code == 250:
                return normalized_email
            if code in (550, 551, 553):
                raise EmailValidationError(f"Mailbox rejected: {code} {message}")
            last_error = f"{code} {message}"
        except (aiosmtplib.SMTPException, OSError) as e:
            last_error = str(e)
            continue
        finally:
            try:
                if verify_client.is_connected:
                    await verify_client.quit()
            except Exception:
                pass

    rmq_logger.warning(
        "Mailbox verification inconclusive for %s: %s", normalized_email, last_error
    )
    return normalized_email


async def send_email(content: NotificationContent):
    rmq_logger.info("Sending email...")

    try:
        recipient = await validate_email("jo.muhsen3@gmail.com")
    except EmailValidationError as e:
        rmq_logger.error(
            "Refusing to send — invalid recipient %s: %s", "jo.muhsen3@gmail.com", e
        )
        return False

    message = EmailMessage()
    message["From"] = settings.SMTP_USERNAME
    message["To"] = recipient
    message["Subject"] = content.subject

    message.set_content(content.body)

    smtp_params = {
        "hostname": settings.SMTP_HOSTNAME,
        "port": settings.SMTP_PORT,
        "use_tls": settings.SMTP_USE_TLS,
        "start_tls": settings.SMTP_START_TLS,
        "username": settings.SMTP_USERNAME,
        "password": settings.SMTP_PASSWORD,
    }
    async for attempt in retry_context(on=aiosmtplib.SMTPException, attempts=3):
        with attempt:
            try:
                smtp_client = aiosmtplib.SMTP(**smtp_params)
                await smtp_client.connect()
                rmq_logger.info("Connected to SMTP server...")
                await smtp_client.send_message(message)
                rmq_logger.info("Message sent...")
                await smtp_client.quit()
                rmq_logger.info("Email sent successfully!")
                return True
            except aiosmtplib.SMTPException as e:
                rmq_logger.error(f"Attempt {attempt.num} failed due to HTTPError: {e}")
                await smtp_client.quit()
                if attempt.num >= 3:
                    return False
                raise
