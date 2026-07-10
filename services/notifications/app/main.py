from fastapi import FastAPI
from app.db.database import create_db_and_tables , SessionDep
from contextlib import asynccontextmanager



# @asynccontextmanager
# async def lifespan(app:FastAPI):
#     create_db_and_tables()
#     yield

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}