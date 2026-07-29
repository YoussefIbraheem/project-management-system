import asyncio
import json

import aio_pika
from aio_pika.exchange import ExchangeType

from app import rmq_logger
from app.core.config import settings
from app.dispatchers import dispatch


async def callback(message: aio_pika.abc.AbstractIncomingMessage):
    async with message.process():
        try:
            body_json = json.loads(message.body.decode("utf-8"))
            data = body_json["args"][0]
            rmq_logger.info("Processing message...")
            rmq_logger.info(f"DATA: {data}")
            dispatch(data)
            rmq_logger.info("Message processed successfully")
        except Exception as e:
            rmq_logger.info(f"Error processing message: {e}")


async def record_activity():
    rmq_logger.info("Recording activity...")

    connection = await aio_pika.connect_robust(settings.BROKER_URL)
    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=100)
        await channel.declare_exchange(
            "mainnotificationsexchange", type=ExchangeType.DIRECT
        )
        await channel.declare_exchange("mainnotificationsdlx", type=ExchangeType.FANOUT)
        main_queue = await channel.declare_queue(
            "mainnotificationsexchangequeue",
            arguments={
                "x-dead-letter-exchange": "mainnotificationsdlx",
                "x-message-ttl": 1000,
            },
        )

        await main_queue.bind("mainnotificationsexchange", routing_key="notifications")

        dlx_queue = await channel.declare_queue("mainnotificationsdlxqueue")
        await dlx_queue.bind("mainnotificationsdlx", routing_key="notifications")

        await dlx_queue.consume(callback)
        rmq_logger.info("Listening for messages...")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(record_activity())
