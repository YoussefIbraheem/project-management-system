from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from app import logger
from app.apis.user_replica_api import router as user_replica_router
from app.auth.auth_bearer import JWTBearer
from app.core.config import settings
from app.db.database import create_db_and_tables  # type: ignore


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting server...")
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan,dependencies=[Depends(JWTBearer())] ,title="Notification Service API Documentation")

app.include_router(user_replica_router, prefix=f"{settings.API_PREFIX}")
