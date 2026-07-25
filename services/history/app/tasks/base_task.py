import asyncio

from celery import Task

from app.db.database import connect_db


class AsyncDBTask(Task):
    """
    Base task class for all async tasks requiring DB access.
    Ensures Beanie is initialized within the same event loop
    as the task execution, regardless of how many tasks are added.
    """
    abstract = True

    def run_async(self, coro):
        async def _run():
            await connect_db()
            return await coro
        return asyncio.run(_run())