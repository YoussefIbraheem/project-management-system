import asyncio
import json
from unittest.mock import AsyncMock, Mock

import pytest
from app.consumers import history_consumer


class _ProcessContext:
    def __init__(self):
        self.entered = False
        self.exited = False
        self.saw_exception = False

    async def __aenter__(self):
        self.entered = True

    async def __aexit__(self, exc_type, exc, tb):  # noqa: ARG002
        self.exited = True
        self.saw_exception = exc_type is not None
        return True  # swallow here too, so the test controls the assertion


class _Message:
    def __init__(self, body: bytes):
        self.body = body
        self.context = _ProcessContext()

    def process(self):
        return self.context


@pytest.mark.asyncio
async def test_callback_awaits_create_event_directly(monkeypatch):
  
    payload = {
        "id": "1",
        "args": [
            {
                "actor_id": "1",
                "service": "tasks",
                "action": "TASK_CREATE",
                "subject_id": "1",
                "subject_type": "task",
                "metadata": {"task_title": "Build API"},
            }
        ],
    }
    message = _Message(json.dumps(payload).encode("utf-8"))
    create_event = AsyncMock(return_value="event-id-1")
    create_task = Mock()

    monkeypatch.setattr(history_consumer, "create_event", create_event)
    monkeypatch.setattr(history_consumer.asyncio, "create_task", create_task)

    await history_consumer.callback(message)

    create_event.assert_awaited_once_with(payload["args"][0])
    create_task.assert_not_called()
    assert message.context.saw_exception is False


@pytest.mark.asyncio
async def test_callback_reraises_on_malformed_payload():
   
    message = _Message(b"not-json")

    await history_consumer.callback(message)

    assert message.context.entered is True
    assert message.context.exited is True
    assert message.context.saw_exception is True


@pytest.mark.asyncio
async def test_callback_reraises_when_create_event_fails(monkeypatch):

    payload = {"id": "1", "args": [{"service": "tasks"}]}
    message = _Message(json.dumps(payload).encode("utf-8"))
    monkeypatch.setattr(
        history_consumer, "create_event", AsyncMock(side_effect=ValueError("bad event"))
    )

    await history_consumer.callback(message)

    assert message.context.saw_exception is True


@pytest.mark.asyncio
async def test_record_activity_consumes_both_the_main_and_dlx_queue(monkeypatch):
    consume = AsyncMock()

    class FakeQueue:
        def __init__(self, name):
            self.name = name

        async def bind(self, *args, **kwargs):  # noqa: ARG002
            return None

        async def consume(self, callback):
            await consume(self.name, callback)

    class FakeChannel:
        def __init__(self):
            self.qos = None
            self.declared_queues = {}

        async def set_qos(self, prefetch_count):
            self.qos = prefetch_count

        async def declare_exchange(self, *args, **kwargs):  # noqa: ARG002
            return None

        async def declare_queue(self, name, *args, **kwargs):  # noqa: ARG002
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

        async def __aexit__(self, exc_type, exc, tb):  # noqa: ARG002
            return None

    fake_connection = FakeConnection()
    monkeypatch.setattr(history_consumer, "connect_db", AsyncMock(return_value=None))
    monkeypatch.setattr(
        history_consumer.aio_pika, "connect_robust", AsyncMock(return_value=fake_connection)
    )

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(history_consumer.record_activity(), timeout=0.05)

    assert consume.call_count == 2, "both main_queue and dlx_queue must be consumed"
    consumed_queues = {call.args[0] for call in consume.call_args_list}
    assert consumed_queues == {"mainhistoryexchangequeue", "mainhistorydlxqueue"}
    for call in consume.call_args_list:
        assert call.args[1] is history_consumer.callback
    assert fake_connection.channel_obj.qos == 100
