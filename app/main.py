from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import EmailStr
from sqlmodel import Session, SQLModel, create_engine, select
from contextlib import asynccontextmanager
from app.models import Feedback


class FeedbackDto:
    name: str
    email: EmailStr
    message: str


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/feedback/")
def create_feedback(feedback_dto: FeedbackDto, session: SessionDep):
    feedback = Feedback(
        name=feedback_dto.name,
        email=feedback_dto.email,
        message=feedback_dto.message)
    session.add(feedback)
    session.commit()
    session.refresh(feedback)
    return feedback


@app.get("/feedback/")
def read_feedbacks(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Feedback]:
    feedback = session.exec(select(Feedback).offset(offset).limit(limit)).all()
    return feedback


@app.get("/feedback/{feedback_id}")
def read_feedback(feedback_id: int, session: SessionDep) -> Feedback:
    feedback = session.get(Feedback, feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return feedback
