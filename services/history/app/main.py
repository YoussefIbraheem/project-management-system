import logging

from fastapi import Depends, FastAPI, Request, responses
from app.core.config import settings
from contextlib import asynccontextmanager
from app.db.database import connect_db, close_db
from app.apis.event_api import router as event_router
from typing import AsyncGenerator
from app.auth.auth_bearer import JWTBearer
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


app = FastAPI(lifespan=lifespan)


@app.get("/",dependencies=[Depends(JWTBearer())])
def read_root():
    return {"project_name": settings.PROJECT_NAME}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


app.include_router(event_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> responses.JSONResponse:
    logger.exception("Unhandled error on %s %s: %s", request.method, request.url, exc)
    return responses.JSONResponse(status_code=500, content={"detail": "Internal server error"})
