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
        self.saw_exception = False

    async def __aenter__(self):
        self.entered = True

    async def __aexit__(self, exc_type, exc, tb):
        self.exited = True
        self.saw_exception = exc_type is not None
        return True  # swallow here too, so the test controls the assertion


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
async def test_callback_awaits_dispatch_directly(monkeypatch):

    dispatch = AsyncMock()
    monkeypatch.setattr(notifications_consumer, "dispatch", dispatch)
    payload = _payload()
    message = _Message(json.dumps(payload).encode("utf-8"))

    await notifications_consumer.callback(message)

    # The dispatcher receives args[0], not the whole envelope.
    dispatch.assert_awaited_once_with(payload["args"][0])
    assert message.context.saw_exception is False


@pytest.mark.asyncio
async def test_callback_reraises_on_malformed_payload(monkeypatch):
    
    dispatch = AsyncMock()
    monkeypatch.setattr(notifications_consumer, "dispatch", dispatch)
    message = _Message(b"not-json")

    await notifications_consumer.callback(message)

    dispatch.assert_not_called()
    assert message.context.exited is True
    assert message.context.saw_exception is True


@pytest.mark.asyncio
async def test_callback_reraises_when_dispatch_fails(monkeypatch):

    dispatch = AsyncMock(side_effect=RuntimeError("handler blew up"))
    monkeypatch.setattr(notifications_consumer, "dispatch", dispatch)
    message = _Message(json.dumps(_payload()).encode("utf-8"))

    await notifications_consumer.callback(message)

    assert message.context.saw_exception is True


@pytest.mark.asyncio
async def test_record_activity_consumes_both_the_main_and_dlx_queue(monkeypatch):
    consume = AsyncMock()

    class FakeQueue:
        def __init__(self, name):
            self.name = name

        async def bind(self, *args, **kwargs):
            return None

        async def consume(self, callback):
            await consume(self.name, callback)

    class FakeChannel:
        def __init__(self):
            self.qos = None
            self.declared_queues = {}

        async def set_qos(self, prefetch_count):
            self.qos = prefetch_count

        async def declare_exchange(self, *args, **kwargs):
            return None

        async def declare_queue(self, name, *args, **kwargs):
            queue = FakeQueue(name)
            self.declared_queues[name] = queue
            return queue

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

    assert consume.call_count == 2, "both main_queue and dlx_queue must be consumed"
    consumed = {call.args[0]: call.args[1] for call in consume.call_args_list}
    assert consumed == {
        "mainnotificationsexchangequeue": notifications_consumer.callback,
        "mainnotificationsdlxqueue": notifications_consumer.dlx_callback,
    }
    assert connection.channel_obj.qos == 100


@pytest.mark.asyncio
async def test_dlx_callback_logs_and_swallows_when_processing_fails_again(monkeypatch):
    dispatch = AsyncMock(side_effect=RuntimeError("still broken"))
    monkeypatch.setattr(notifications_consumer, "dispatch", dispatch)
    message = _Message(json.dumps(_payload()).encode("utf-8"))
    error_log = Mock()
    monkeypatch.setattr(notifications_consumer.rmq_logger, "error", error_log)

    await notifications_consumer.dlx_callback(message)

    assert message.context.saw_exception is False, (
        "a second failure must not propagate - there's no further dead-letter target"
    )
    error_log.assert_called_once()
