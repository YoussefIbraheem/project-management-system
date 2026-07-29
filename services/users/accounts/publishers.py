import json
import logging
import os
import uuid

import environ
import pika
from pika.exchange_type import ExchangeType

env = environ.Env()
env.read_env(os.path.join(os.path.dirname(__file__), ".env"))
logger = logging.getLogger(__name__)


def _fetch_connection_params():
    params = pika.ConnectionParameters(
        host=env.str("RABBITMQ_HOST"),
        port=env.int("RABBITMQ_PORT"),
        virtual_host="/",
        credentials=pika.PlainCredentials(
            username=env.str("RABBITMQ_USER"),
            password=env.str("RABBITMQ_PASSWORD"),
        ),
    )
    return params


def publish_history_event(event_data):
    try:
        logger.info(f"Publishing history event: {event_data}")
        data = {
            "task": "app.consumers.history_consumer.record_activity",
            "id": str(uuid.uuid4()),
            "args": [event_data],
            "kwargs": {},
            "retries": 0,
        }

        params = _fetch_connection_params()
        message = json.dumps(data).encode("utf-8")
        with pika.BlockingConnection(params) as conn:
            with conn.channel() as channel:
                channel.exchange_declare(
                    exchange="mainhistoryexchange", exchange_type=ExchangeType.direct
                )
                channel.basic_publish(
                    exchange="mainhistoryexchange", routing_key="history", body=message
                )
        logger.info("History event published successfully.")
    except Exception as e:
        logger.error(f"Error publishing history event: {e}", exc_info=True)
        raise


def publish_notification_event(event_data):
    try:
        logger.info(f"Publishing notifications event: {event_data}")
        params = _fetch_connection_params()
        data = {
            "task": "app.consumers.notification_consumer.record_activity",
            "id": str(uuid.uuid4()),
            "args": [event_data],
            "kwargs": {},
            "retries": 0,
        }
        message = json.dumps(data).encode("utf-8")
        with pika.BlockingConnection(params) as conn:
            with conn.channel() as channel:
                channel.exchange_declare(
                    exchange="mainnotificationsexchange", exchange_type=ExchangeType.direct
                )
                channel.basic_publish(
                    exchange="mainnotificationsexchange", routing_key="notifications", body=message
                )
                logger.info("Notifications event published successfully.")
    except Exception as e:
        logger.error(f"Error publishing notifications event: {e}", exc_info=True)
        raise
