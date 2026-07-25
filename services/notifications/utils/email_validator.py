import aiosmtplib
import dns.asyncresolver
import dns.resolver
from app import rmq_logger
from app.core.config import settings
from email_validator import EmailNotValidError
from email_validator import validate_email as _validate_syntax


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