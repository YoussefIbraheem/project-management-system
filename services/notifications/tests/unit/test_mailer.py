import logging
from types import SimpleNamespace
from typing import ClassVar

import aiosmtplib
import pytest
import stamina
from app.models.email_log import EmailStatus
from app.services.email_log_service import list_email_logs
from app.templates import NotificationContent
from utils import mailer
from utils.email_validator import EmailValidationError


@pytest.fixture(autouse=True)
def no_retry_backoff():
    """stamina sleeps between attempts; disable that but keep retry counts."""
    with stamina.set_testing(True, attempts=3):
        yield


@pytest.fixture(autouse=True)
def stub_email_validation(monkeypatch):
    async def _validate(email):
        return email

    monkeypatch.setattr(mailer, "validate_email", _validate)


@pytest.fixture()
def settings():
    return SimpleNamespace(
        SMTP_HOSTNAME="smtp.test",
        SMTP_PORT=587,
        SMTP_USE_TLS=False,
        SMTP_START_TLS=True,
        SMTP_USERNAME="sender@test",
        SMTP_PASSWORD="secret",
        SMTP_MAX_ATTEMPTS=3,
    )


class FakeSMTP:
    """Records the SMTP conversation; optionally fails the first N sends."""

    instances: ClassVar = []

    def __init__(self, failures=0, fail_on_connect=False, **params):
        self.params = params
        self.failures = failures
        self.fail_on_connect = fail_on_connect
        self.sent = []
        self.is_connected = False
        self.quit_called = False
        FakeSMTP.instances.append(self)

    async def connect(self):
        if self.fail_on_connect and FakeSMTP.attempts_made() <= self.failures:
            raise aiosmtplib.SMTPException("connect failed")
        self.is_connected = True

    async def send_message(self, message):
        if not self.fail_on_connect and FakeSMTP.attempts_made() <= self.failures:
            raise aiosmtplib.SMTPException("send failed")
        self.sent.append(message)

    async def quit(self):
        self.quit_called = True
        self.is_connected = False

    @classmethod
    def attempts_made(cls):
        return len(cls.instances)


@pytest.fixture()
def smtp_factory():
    FakeSMTP.instances = []

    def _factory(failures=0, fail_on_connect=False):
        def build(**params):
            return FakeSMTP(
                failures=failures, fail_on_connect=fail_on_connect, **params
            )

        return build

    return _factory


@pytest.fixture()
def service(settings, smtp_factory):
    def _build(failures=0, fail_on_connect=False):
        return mailer.EmailService(
            settings=settings,
            logger=logging.getLogger("test-mailer"),
            smtp_client_factory=smtp_factory(failures, fail_on_connect),
        )

    return _build


@pytest.fixture()
def content():
    return NotificationContent(
        subject="Welcome",
        body="Hello there",
        recipient_email="recipient@test",
        notification_id=None,
    )


@pytest.fixture()
def logged_content(session):
    """Content tied to a real notification row so email logs can be written."""
    from app.models.notification import Notification
    from app.models.user_replica import UserReplica

    session.add(
        UserReplica(
            user_id="1", username="alice", email="alice@test", display_name="Alice"
        )
    )
    notification = Notification(
        user_id="1", type="TASK_CREATE", subject="Welcome", body="Hello there"
    )
    session.add(notification)
    session.commit()
    session.refresh(notification)

    return NotificationContent(
        subject="Welcome",
        body="Hello there",
        recipient_email="recipient@test",
        notification_id=notification.id,
    )


@pytest.mark.asyncio
async def test_sends_message_and_reports_success(service, content):
    result = await service().send_email(content)

    assert result is True
    assert len(FakeSMTP.instances) == 1
    message = FakeSMTP.instances[0].sent[0]
    assert message["To"] == "recipient@test"
    assert message["Subject"] == "Welcome"


@pytest.mark.asyncio
async def test_passes_configured_smtp_params(service, content, settings):
    await service().send_email(content)

    params = FakeSMTP.instances[0].params
    assert params["hostname"] == settings.SMTP_HOSTNAME
    assert params["port"] == settings.SMTP_PORT
    assert params["username"] == settings.SMTP_USERNAME
    assert params["start_tls"] == settings.SMTP_START_TLS


@pytest.mark.asyncio
async def test_closes_connection_after_sending(service, content):
    await service().send_email(content)

    assert FakeSMTP.instances[0].quit_called is True


@pytest.mark.asyncio
async def test_refuses_to_send_to_invalid_recipient(service, content, monkeypatch):
    async def _reject(email):
        raise EmailValidationError("no such mailbox")

    monkeypatch.setattr(mailer, "validate_email", _reject)

    result = await service().send_email(content)

    assert result is False
    assert FakeSMTP.instances == [], (
        "must not open an SMTP connection for a bad address"
    )


@pytest.mark.asyncio
async def test_no_email_log_written_without_notification_id(service, content, session):
    await service().send_email(content)

    assert list_email_logs() == []


@pytest.mark.asyncio
async def test_successful_send_logs_sent_status(service, logged_content):
    result = await service().send_email(logged_content)

    assert result is True
    logs = list_email_logs()
    assert len(logs) == 1
    assert logs[0].status == EmailStatus.SENT.value
    assert logs[0].attempts == 1
    assert logs[0].sent_at is not None


@pytest.mark.asyncio
async def test_retries_after_send_failure_then_succeeds(service, logged_content):
    result = await service(failures=1).send_email(logged_content)

    assert result is True
    assert len(FakeSMTP.instances) == 2, "should have retried once"
    logs = list_email_logs()
    assert len(logs) == 1, "retries update the original log rather than adding rows"
    assert logs[0].status == EmailStatus.SENT.value
    assert logs[0].attempts == 2


@pytest.mark.asyncio
async def test_exhausting_attempts_records_failure(service, logged_content):
    result = await service(failures=99).send_email(logged_content)

    assert result is False
    logs = list_email_logs()
    assert len(logs) == 1
    assert logs[0].status == EmailStatus.FAILED.value
    assert logs[0].error_message


@pytest.mark.asyncio
async def test_retry_after_connect_failure_still_logs(service, logged_content):
    """Regression: a first-attempt connect() failure must not break the retry.

    The log is created before connecting, so a connection that never opens is
    still recorded and the retry has a row to update instead of dereferencing
    None.
    """
    result = await service(failures=1, fail_on_connect=True).send_email(logged_content)

    assert result is True
    logs = list_email_logs()
    assert len(logs) == 1
    assert logs[0].status == EmailStatus.SENT.value
    assert logs[0].attempts == 2


@pytest.mark.asyncio
async def test_connection_failure_is_recorded_even_when_never_established(
    service, logged_content
):
    """The log is a record of the attempt, not of a successful connection."""
    result = await service(failures=99, fail_on_connect=True).send_email(logged_content)

    assert result is False
    logs = list_email_logs()
    assert len(logs) == 1
    assert logs[0].status == EmailStatus.FAILED.value
    assert logs[0].error_message


@pytest.mark.asyncio
async def test_failure_is_recorded_when_stamina_stops_before_max_attempts(
    service, logged_content
):
    """stamina ends a retry run on its `timeout` budget as well as on attempts.

    retry_context defaults to timeout=45s, and aiosmtplib's own connect timeout
    is 60s, so two slow connections can exhaust the budget before attempt 3.
    Simulated here by letting stamina make 2 attempts while settings still say
    3 — the `attempt.num >= SMTP_MAX_ATTEMPTS` check never matches.
    """
    with stamina.set_testing(True, attempts=2):  # settings.SMTP_MAX_ATTEMPTS is 3
        result = await service(failures=99).send_email(logged_content)

    assert result is False, "caller must be told the send failed"
    logs = list_email_logs()
    assert logs[0].status == EmailStatus.FAILED.value
