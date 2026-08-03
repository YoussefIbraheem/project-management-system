from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app import logger
from app.apis.email_log_api import router as email_log_router
from app.apis.notification_api import router as notifications_router
from app.apis.user_replica_api import router as user_replica_router
from app.auth.auth_bearer import JWTBearer
from app.core.config import settings
from app.db.database import create_db_and_tables  # type: ignore


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting server...")
    create_db_and_tables()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Notification Service API Documentation",
)

app.include_router(user_replica_router, prefix=f"{settings.API_PREFIX}",tags=["User Replica"])
app.include_router(notifications_router, prefix=f"{settings.API_PREFIX}",tags=["Notifications"])
app.include_router(email_log_router, prefix=f"{settings.API_PREFIX}",tags=["Email Log"])

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