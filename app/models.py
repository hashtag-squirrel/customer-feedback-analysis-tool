from sqlmodel import SQLModel, Field
from pydantic import EmailStr


class Feedback(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: EmailStr
    message: str
    processed: bool
    sentiment: str
    topics: str
