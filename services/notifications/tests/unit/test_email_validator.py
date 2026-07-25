import asyncio
from types import SimpleNamespace

import aiosmtplib
import dns.resolver
import pytest
from email_validator import EmailNotValidError
from utils import email_validator as validator


class FakeMXAnswer:
    def __init__(self, exchange: str, preference: int):
        self.exchange = exchange
        self.preference = preference


class FakeResolver:
    def __init__(self, responses):
        self.responses = responses
        self.timeout = None
        self.lifetime = None

    async def resolve(self, domain, record):
        outcome = self.responses[(domain, record)]
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


class FakeSMTP:
    behaviors = {}
    instances = []

    def __init__(self, hostname, port, timeout):
        self.hostname = hostname
        self.port = port
        self.timeout = timeout
        self.is_connected = False
        self.quit_called = False
        FakeSMTP.instances.append(self)

    async def connect(self):
        self.is_connected = True

    async def helo(self):
        return None

    async def mail(self, sender):
        self.sender = sender

    async def rcpt(self, recipient):
        behavior = self.behaviors[self.hostname]
        if isinstance(behavior, Exception):
            raise behavior
        return behavior

    async def quit(self):
        self.quit_called = True
        self.is_connected = False


@pytest.fixture(autouse=True)
def reset_fake_smtp():
    FakeSMTP.behaviors = {}
    FakeSMTP.instances = []


def test_resolve_mx_hosts_sorts_and_strips_trailing_dot(monkeypatch):
    fake_answers = [
        FakeMXAnswer("mx2.example.com.", 20),
        FakeMXAnswer("mx1.example.com.", 10),
    ]
    fake_resolver = FakeResolver({("example.com", "MX"): fake_answers})
    monkeypatch.setattr(validator.dns.asyncresolver, "Resolver", lambda: fake_resolver)
    monkeypatch.setattr(validator.settings, "DNS_TIMEOUT", 1)

    hosts = asyncio.run(validator._resolve_mx_hosts("example.com"))

    assert hosts == ["mx1.example.com", "mx2.example.com"]


def test_resolve_mx_hosts_falls_back_to_a_record(monkeypatch):
    fake_resolver = FakeResolver(
        {
            ("example.com", "MX"): dns.resolver.NoAnswer(),
            ("example.com", "A"): [SimpleNamespace()],
        }
    )
    monkeypatch.setattr(validator.dns.asyncresolver, "Resolver", lambda: fake_resolver)
    monkeypatch.setattr(validator.settings, "DNS_TIMEOUT", 1)

    hosts = asyncio.run(validator._resolve_mx_hosts("example.com"))

    assert hosts == ["example.com"]


def test_resolve_mx_hosts_raises_for_missing_domain(monkeypatch):
    fake_resolver = FakeResolver(
        {("missing.example", "MX"): dns.resolver.NXDOMAIN()}
    )
    monkeypatch.setattr(validator.dns.asyncresolver, "Resolver", lambda: fake_resolver)
    monkeypatch.setattr(validator.settings, "DNS_TIMEOUT", 1)

    with pytest.raises(validator.EmailValidationError, match="Domain does not exist"):
        asyncio.run(validator._resolve_mx_hosts("missing.example"))


def test_validate_email_rejects_bad_syntax(monkeypatch):
    monkeypatch.setattr(
        validator,
        "_validate_syntax",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(EmailNotValidError("bad")),
    )

    with pytest.raises(validator.EmailValidationError, match="Bad syntax"):
        asyncio.run(validator.validate_email("not-an-email"))


def test_validate_email_returns_normalized_email(monkeypatch):
    monkeypatch.setattr(
        validator,
        "_validate_syntax",
        lambda *_args, **_kwargs: SimpleNamespace(
            normalized="Alice@example.com", domain="example.com"
        ),
    )
    monkeypatch.setattr(
        validator.dns.asyncresolver,
        "Resolver",
        lambda: FakeResolver({("example.com", "MX"): [FakeMXAnswer("mx1.example.com.", 10)]}),
    )
    monkeypatch.setattr(validator.settings, "DNS_TIMEOUT", 1)
    monkeypatch.setattr(validator.settings, "SMTP_VERIFY_TIMEOUT", 1)
    monkeypatch.setattr(validator.settings, "SMTP_USERNAME", "sender@example.com")
    monkeypatch.setattr(validator.aiosmtplib, "SMTP", FakeSMTP)
    FakeSMTP.behaviors = {"mx1.example.com": (250, "OK")}

    normalized = asyncio.run(validator.validate_email("alice@example.com"))

    assert normalized == "Alice@example.com"
    assert len(FakeSMTP.instances) == 1
    assert FakeSMTP.instances[0].quit_called is True


def test_validate_email_uses_next_host_on_smtp_error(monkeypatch):
    monkeypatch.setattr(
        validator,
        "_validate_syntax",
        lambda *_args, **_kwargs: SimpleNamespace(
            normalized="Alice@example.com", domain="example.com"
        ),
    )
    monkeypatch.setattr(
        validator.dns.asyncresolver,
        "Resolver",
        lambda: FakeResolver(
            {
                (
                    "example.com",
                    "MX",
                ): [
                    FakeMXAnswer("mx1.example.com.", 10),
                    FakeMXAnswer("mx2.example.com.", 20),
                ]
            }
        ),
    )
    monkeypatch.setattr(validator.settings, "DNS_TIMEOUT", 1)
    monkeypatch.setattr(validator.settings, "SMTP_VERIFY_TIMEOUT", 1)
    monkeypatch.setattr(validator.settings, "SMTP_USERNAME", "sender@example.com")
    monkeypatch.setattr(validator.aiosmtplib, "SMTP", FakeSMTP)
    FakeSMTP.behaviors = {
        "mx1.example.com": aiosmtplib.SMTPException("temporary failure"),
        "mx2.example.com": (250, "OK"),
    }

    normalized = asyncio.run(validator.validate_email("alice@example.com"))

    assert normalized == "Alice@example.com"
    assert [client.hostname for client in FakeSMTP.instances] == [
        "mx1.example.com",
        "mx2.example.com",
    ]


def test_validate_email_raises_on_mailbox_rejection(monkeypatch):
    monkeypatch.setattr(
        validator,
        "_validate_syntax",
        lambda *_args, **_kwargs: SimpleNamespace(
            normalized="Alice@example.com", domain="example.com"
        ),
    )
    monkeypatch.setattr(
        validator.dns.asyncresolver,
        "Resolver",
        lambda: FakeResolver({("example.com", "MX"): [FakeMXAnswer("mx1.example.com.", 10)]}),
    )
    monkeypatch.setattr(validator.settings, "DNS_TIMEOUT", 1)
    monkeypatch.setattr(validator.settings, "SMTP_VERIFY_TIMEOUT", 1)
    monkeypatch.setattr(validator.settings, "SMTP_USERNAME", "sender@example.com")
    monkeypatch.setattr(validator.aiosmtplib, "SMTP", FakeSMTP)
    FakeSMTP.behaviors = {"mx1.example.com": (550, "Mailbox unavailable")}

    with pytest.raises(validator.EmailValidationError, match="Mailbox rejected"):
        asyncio.run(validator.validate_email("alice@example.com"))
