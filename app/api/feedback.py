from typing import Annotated
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from sqlmodel import select
from app.models.feedback import Feedback, FeedbackUpdate
from app.database import SessionDep, session_scope
from app.clients.ai_client import OpenAiClient
from app.clients.notify_client import NtfyNotifyClient


feedback_router = APIRouter(prefix="/feedback")
ai_client = OpenAiClient()
notify_client = NtfyNotifyClient()


@feedback_router.post("/")
def create_feedback(
    feedback_update: FeedbackUpdate,
    session: SessionDep,
    background: BackgroundTasks
) -> Feedback:

    feedback = Feedback(
        name=feedback_update.name,
        email=feedback_update.email,
        message=feedback_update.message)
    session.add(feedback)
    session.commit()
    session.refresh(feedback)
    background.add_task(analyze_one_feedback, feedback.id)
    return feedback


@feedback_router.get("/")
def read_feedbacks(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Feedback]:
    feedbacks = session.exec(
        select(Feedback).offset(offset).limit(limit)).all()
    return feedbacks


@feedback_router.get("/{feedback_id}")
def read_feedback(feedback_id: int, session: SessionDep) -> Feedback:
    feedback = session.get(Feedback, feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return feedback


def analyze_one_feedback(feedback_id: int) -> None:
    with session_scope() as session:
        feedback = session.get(Feedback, feedback_id)
        if not feedback:
            return
        response = ai_client.analyze_feedback(feedback.message)
        sentiment = response['sentiment']
        topics = response['topics']
        feedback.processed = True
        feedback.sentiment = sentiment
        feedback.topics = topics

        if sentiment == 'negative':
            notify_client.notify_team(feedback)

        try:
            session.commit()
        except Exception:
            session.rollback()
            raise


def check_unprocessed_feedback(
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> None:
    with session_scope() as session:
        feedbacks = session.exec(
            select(Feedback).offset(offset).limit(limit)).all()
        [analyze_one_feedback(fb.id) for fb in feedbacks if not fb.processed]
