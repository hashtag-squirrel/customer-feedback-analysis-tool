from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query, BackgroundTasks
from pydantic import EmailStr, BaseModel
from sqlmodel import Session, SQLModel, create_engine, select
from contextlib import asynccontextmanager
from app.models import Feedback
from app.ai_app import get_ai_response


class FeedbackDto(BaseModel):
    name: str
    email: EmailStr
    message: str


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def session_scope() -> Session:
    return Session(engine)


SessionDep = Annotated[Session, Depends(session_scope)]


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


def analyze_one_feedback(feedback_id: int) -> None:
    with session_scope() as session:
        fb = session.get(Feedback, feedback_id)
        if not fb:
            return
        response = get_ai_response(fb.message)
        sentiment = response['sentiment']
        topic = response['topics']
        fb.processed = True
        fb.sentiment = sentiment
        fb.topics = topic
        try:
            session.commit()
        except Exception:
            session.rollback()
            raise

    with session_scope() as verify_session:
        verify_fb = verify_session.get(Feedback, feedback_id)
        print("verify:", verify_fb.processed, verify_fb.sentiment, verify_fb.topics)

@app.post("/feedback/")
def create_feedback(feedback_dto: FeedbackDto, session: SessionDep, background: BackgroundTasks):
    feedback = Feedback(
        name=feedback_dto.name,
        email=feedback_dto.email,
        message=feedback_dto.message)
    session.add(feedback)
    session.commit()
    session.refresh(feedback)
    background.add_task(analyze_one_feedback, feedback.id)
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
