import logging

from beanie import init_beanie
from pymongo import AsyncMongoClient

from app.core.config import settings
from app.models.event import Event

logger = logging.getLogger(__name__)

_client: AsyncMongoClient | None = None


async def connect_db():
    global _client
    
    logger.info("DB_URL used: '%s'.",settings.MONGO_DB_URL)
    _client = AsyncMongoClient(settings.MONGO_DB_URL)
    db = _client.get_database(settings.MONGO_DB_NAME)
    print(f"connecting to {db}")
    await init_beanie(database=db, document_models=[Event])
    logger.info("Beanie initialised against database '%s'.", settings.MONGO_DB_NAME)


async def close_db() -> None:
    global _client
    if _client is not None:
        await _client.close()
        _client = None
        logger.info("DocumentDB client closed.")
