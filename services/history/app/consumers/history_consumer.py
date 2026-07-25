import asyncio
import json
import logging

import aio_pika
import aio_pika.abc
from aio_pika import logger

from app.core.config import settings
from app.db.database import connect_db
from app.services.event_service import create_event

logger.setLevel(logging.INFO)

async def callback(message: aio_pika.abc.AbstractIncomingMessage):
    async with message.process():
        try:
            body_json = json.loads(message.body.decode('utf-8'))
            data = body_json["args"][0]
            print("Processing message...")
            print(f'event_id:{body_json["id"]}')
            print(f"event_type: {data['action']}")
            asyncio.create_task(create_event(data))
            print("Message processed successfully")
        except Exception as e:
            print(f"Error processing message: {e}")



async def record_activity():
   print("Recording activity...")
   await connect_db()
   connection = await aio_pika.connect_robust(settings.RABBITMQ_BROKER_URL)
   async with connection:
       channel = await connection.channel()
       await channel.set_qos(prefetch_count=100)
       queue = await channel.declare_queue(
                  "history",
                  durable=True,
                  arguments= {"x-dead-letter-exchange": "dlx","x-dead-letter-routing-key": "history.failed",}
        )
       await queue.consume(callback)
       print("Listening for messages...")
       await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(record_activity())
