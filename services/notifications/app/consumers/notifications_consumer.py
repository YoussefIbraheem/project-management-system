import asyncio
import json

import aio_pika

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
        queue = await channel.declare_queue(
            "notifications",
            durable=True,
            arguments={
                "x-dead-letter-exchange": "dlx",
                "x-dead-letter-routing-key": "notifications.failed",
            },
        )
        await queue.consume(callback)
        rmq_logger.info("Listening for messages...")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(record_activity())
