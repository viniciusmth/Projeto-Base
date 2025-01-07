from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.settings import Settings

engine = create_engine(Settings().DATABASE_URL)


def init_session():
    with Session(engine) as session:
        yield session
