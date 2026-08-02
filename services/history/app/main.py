import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request, responses
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

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


app = FastAPI(
    lifespan=lifespan,
    title="History Service API Documentation",
)

allowed_origins = [settings.CORS_ALLOWED_ORIGINS]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/admin/")
def admin():
    return RedirectResponse(settings.ADMIN_USER_MODEL)


# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: str | None = None):
#     return {"item_id": item_id, "q": q}


app.include_router(event_router, prefix=settings.API_PREFIX)


@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request, exc: Exception
) -> responses.JSONResponse:
    logger.exception("Unhandled error on %s %s: %s", request.method, request.url, exc)
    return responses.JSONResponse(
        status_code=500, content={"detail": "Internal server error"}
    )
