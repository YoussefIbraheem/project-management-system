import json
import uuid

import pika
from app import logger, settings
from .event import Event

def publish_history_event(event: Event):
    """Publish a new history event."""
    
    try:
        with pika.BlockingConnection(
            pika.URLParameters(settings.BROKER_URL)
        ) as connection:
            channel = connection.channel()
            event_data = event.to_dict()
            logger.info("Publishing new history event...")
            logger.info(f"Event: {event_data}")
            channel.basic_publish(
                exchange="",
                routing_key="history",
                body=json.dumps(
                    {
                        "task": "app.consumers.history_consumer.record_activity",
                        "id": str(uuid.uuid4()),
                        "args": [event_data],
                        "kwargs": {},
                        "retries": 0,
                    }
                ),
                properties=pika.BasicProperties(
                    content_type="application/json",
                    delivery_mode=2,
                ),
            )
            logger.info(
                f"History event for action {event_data['action']} model {event_data['service']} published successfully."
            )
    except Exception as e:
        logger.error(f"Failed to publish history event:{e}", exc_info=True)
