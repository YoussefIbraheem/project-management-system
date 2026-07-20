from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.apis.user_replica_api import router as user_replica_router
from app.db.database import create_db_and_tables #type: ignore
from app import logger

@asynccontextmanager
async def lifespan(app:FastAPI):
    logger.info("Starting server...")
    create_db_and_tables() 
    yield
    

app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


app.include_router(user_replica_router)

