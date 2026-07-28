"""Tests for the notifications RabbitMQ consumer.

The history service has equivalent coverage for its consumer; this closes the
same gap on the notifications side. The broker itself is faked — end-to-end
delivery is proven by tests/integration at the repo root.
"""

import asyncio
import json
from unittest.mock import AsyncMock, Mock

import pytest
from app.consumers import notifications_consumer  # type: ignore


class _ProcessContext:
    def __init__(self):
        self.entered = False
        self.exited = False

    async def __aenter__(self):
        self.entered = True

    async def __aexit__(self, exc_type, exc, tb):
        self.exited = True


class _Message:
    def __init__(self, body: bytes):
        self.body = body
        self.context = _ProcessContext()

    def process(self):
        return self.context


def _payload(**overrides):
    data = {
        "actor_id": "1",
        "service": "users",
        "action": "USER_REGISTER",
        "subject_id": "1",
        "subject_type": "users",
        "metadata": {
            "user_id": "1",
            "username": "alice",
            "email": "alice@example.com",
            "display_name": "Alice",
        },
    }
    data.update(overrides)
    return {"id": "evt-1", "args": [data], "kwargs": {}, "retries": 0}


@pytest.mark.asyncio
async def test_callback_unwraps_envelope_and_dispatches(monkeypatch):
    dispatch = Mock()
    monkeypatch.setattr(notifications_consumer, "dispatch", dispatch)
    payload = _payload()
    message = _Message(json.dumps(payload).encode("utf-8"))

    await notifications_consumer.callback(message)

    # The dispatcher receives args[0], not the whole envelope.
    dispatch.assert_called_once_with(payload["args"][0])
    assert message.context.entered is True
    assert message.context.exited is True


@pytest.mark.asyncio
async def test_callback_acks_malformed_payload_without_raising(monkeypatch):
    """A poison message must not escape and kill the consumer loop."""
    dispatch = Mock()
    monkeypatch.setattr(notifications_consumer, "dispatch", dispatch)
    message = _Message(b"not-json")

    await notifications_consumer.callback(message)

    dispatch.assert_not_called()
    assert message.context.exited is True


@pytest.mark.asyncio
async def test_callback_survives_a_failing_dispatcher(monkeypatch):
    dispatch = Mock(side_effect=RuntimeError("handler blew up"))
    monkeypatch.setattr(notifications_consumer, "dispatch", dispatch)
    message = _Message(json.dumps(_payload()).encode("utf-8"))

    await notifications_consumer.callback(message)

    assert message.context.exited is True


@pytest.mark.asyncio
async def test_record_activity_declares_durable_queue_and_consumes(monkeypatch):
    consume = AsyncMock()
    declared = {}

    class FakeQueue:
        async def consume(self, callback):
            await consume(callback)

    class FakeChannel:
        def __init__(self):
            self.qos = None
            self.queue = FakeQueue()

        async def set_qos(self, prefetch_count):
            self.qos = prefetch_count

        async def declare_queue(self, name, **kwargs):
            declared["name"] = name
            declared.update(kwargs)
            return self.queue

    class FakeConnection:
        def __init__(self):
            self.channel_obj = FakeChannel()

        async def channel(self):
            return self.channel_obj

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

    connection = FakeConnection()
    monkeypatch.setattr(
        notifications_consumer.aio_pika,
        "connect_robust",
        AsyncMock(return_value=connection),
    )

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(notifications_consumer.record_activity(), timeout=0.05)

    consume.assert_called_once()
    assert consume.call_args.args[0] is notifications_consumer.callback
    # Queue name and durability must match what the publishers declare.
    assert declared["name"] == "notifications"
    assert declared["durable"] is True
    assert connection.channel_obj.qos == 100
