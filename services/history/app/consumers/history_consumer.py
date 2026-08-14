import asyncio
import json
import logging

import aio_pika
import aio_pika.abc
from aio_pika import logger
from aio_pika.exchange import ExchangeType

from app.core.config import settings
from app.db.database import connect_db
from app.services.event_service import create_event

logger.setLevel(logging.INFO)


async def _process_event(message: aio_pika.abc.AbstractIncomingMessage) -> None:
    body_json = json.loads(message.body.decode("utf-8"))
    data = body_json["args"][0]
    print("Processing message...")
    print(f"event_id:{body_json['id']}")
    print(f"event_type: {data['action']}")
    await create_event(data)
    print("Message processed successfully")


async def callback(message: aio_pika.abc.AbstractIncomingMessage):
    async with message.process():
        try:
            await _process_event(message)
        except Exception as e:
            print(f"Error processing message: {e}")
            raise


async def dlx_callback(message: aio_pika.abc.AbstractIncomingMessage):
    async with message.process():
        try:
            await _process_event(message)
        except Exception as e:
            logger.error(f"Message permanently failed after DLX retry, dropping: {e}")


async def record_activity():
    print("Recording activity...")
    await connect_db()
    connection = await aio_pika.connect_robust(settings.RABBITMQ_BROKER_URL)
    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=100)
        await channel.declare_exchange("mainhistoryexchange", type=ExchangeType.DIRECT)
        await channel.declare_exchange("mainhistorydlx", type=ExchangeType.FANOUT)

        main_queue = await channel.declare_queue(
            "mainhistoryexchangequeue",
            arguments={
                "x-dead-letter-exchange": "mainhistorydlx",
                "x-message-ttl": settings.DLX_TTL,
            },
        )

        await main_queue.bind(
            "mainhistoryexchange",
            routing_key="history",
        )

        dlx_queue = await channel.declare_queue("mainhistorydlxqueue")
        await dlx_queue.bind("mainhistorydlx", routing_key="history")

        await main_queue.consume(callback)
        await dlx_queue.consume(dlx_callback)
        print("Listening for messages...")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(record_activity())
