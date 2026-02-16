from sqlmodel import SQLModel, Field
from pydantic import EmailStr, BaseModel


class Feedback(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: EmailStr
    message: str
    processed: bool | None = Field(default=False)
    sentiment: str | None = Field(default=None)
    topics: str | None = Field(default=None)


class FeedbackUpdate(BaseModel):
    name: str
    email: EmailStr
    message: str
