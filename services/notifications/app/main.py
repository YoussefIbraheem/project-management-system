from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import logger
from app.apis.user_replica_api import router as user_replica_router
from app.core.config import settings
from app.db.database import create_db_and_tables  # type: ignore


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting server...")
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, title="Notification Service API Documentation")


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


app.include_router(user_replica_router, prefix=f"{settings.API_PREFIX}")
