import asyncio
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from app.consumers import history_consumer


class _ProcessContext:
    def __init__(self):
        self.entered = False
        self.exited = False

    async def __aenter__(self):
        self.entered = True

    async def __aexit__(self, exc_type, exc, tb):  # noqa: ARG002
        self.exited = True


class _Message:
    def __init__(self, body: bytes):
        self.body = body
        self.context = _ProcessContext()

    def process(self):
        return self.context


@pytest.mark.asyncio
async def test_callback_processes_message_and_schedules_create_event(monkeypatch):
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
    create_event = Mock(return_value="task-scheduled")
    create_task = Mock(return_value=SimpleNamespace(done=True))

    monkeypatch.setattr(history_consumer, "create_event", create_event)
    monkeypatch.setattr(history_consumer.asyncio, "create_task", create_task)

    await history_consumer.callback(message)

    create_event.assert_called_once_with(payload["args"][0])
    create_task.assert_called_once_with("task-scheduled")
    assert message.context.entered is True
    assert message.context.exited is True


@pytest.mark.asyncio
async def test_callback_swallow_invalid_payload(monkeypatch):
    message = _Message(b"not-json")
    create_task = Mock()
    monkeypatch.setattr(history_consumer.asyncio, "create_task", create_task)

    await history_consumer.callback(message)

    create_task.assert_not_called()
    assert message.context.entered is True
    assert message.context.exited is True


@pytest.mark.asyncio
async def test_record_activity_wires_consumer_and_queue(monkeypatch):
    consume = AsyncMock()

    class FakeQueue:
        async def consume(self, callback):  # noqa: ARG002
            await consume(callback)

    class FakeChannel:
        def __init__(self):
            self.qos = None
            self.queue = FakeQueue()

        async def set_qos(self, prefetch_count):
            self.qos = prefetch_count

        async def declare_queue(self, *args, **kwargs):  # noqa: ARG002
            return self.queue

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
    monkeypatch.setattr(history_consumer.aio_pika, "connect_robust", AsyncMock(return_value=fake_connection))

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(history_consumer.record_activity(), timeout=0.05)

    consume.assert_called_once()
    callback = consume.call_args.args[0]
    assert callback is history_consumer.callback
    assert fake_connection.channel_obj.qos == 100
