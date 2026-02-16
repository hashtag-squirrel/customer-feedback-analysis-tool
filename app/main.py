from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import create_db_and_tables
from app.api.feedback import check_unprocessed_feedback, router


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables()
    check_unprocessed_feedback()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router)
