import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import Depends, FastAPI, Request, responses

from app.apis.event_api import router as event_router
from app.auth.auth_bearer import JWTBearer
from app.core.config import settings
from app.db.database import close_db, connect_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await connect_db()
    yield
    await close_db()


app = FastAPI(lifespan=lifespan, dependencies=[Depends(JWTBearer())])


@app.get("/")
def read_root():
    return {"project_name": settings.PROJECT_NAME}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


app.include_router(event_router)


@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request, exc: Exception
) -> responses.JSONResponse:
    logger.exception("Unhandled error on %s %s: %s", request.method, request.url, exc)
    return responses.JSONResponse(
        status_code=500, content={"detail": "Internal server error"}
    )
