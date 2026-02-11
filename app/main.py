from fastapi import FastAPI
from pydantic import BaseModel, EmailStr

app = FastAPI()


class Feedback(BaseModel):
    name: str
    email: EmailStr
    message: str


@app.get("/feedback/{feedback_id}")
def read_feedback(feedback: Feedback):
    return {
        'name': feedback.name,
        'email': feedback.email,
        'message': feedback.message
    }


@app.post("/feedback/")
def create_feedback(feedback: Feedback):
    return {
        'name': feedback.name,
        'email': feedback.email,
        'message': feedback.message
    }
