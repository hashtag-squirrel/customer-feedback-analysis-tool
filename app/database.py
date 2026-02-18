from fastapi import Depends
from typing import Annotated
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.engine import Engine
import os


database_path: str = os.environ.get(key='DATABASE_PATH', default='/database')
sqlite_file_name: str = "database.db"
sqlite_url: str = f"sqlite:///{database_path}/{sqlite_file_name}"

connect_args: dict[str, bool] = {"check_same_thread": False}
engine: Engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def session_scope() -> Session:
    return Session(engine)


SessionDep = Annotated[Session, Depends(session_scope)]
