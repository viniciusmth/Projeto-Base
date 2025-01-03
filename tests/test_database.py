from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from backend.models import User, mapper_registry


def test_create_user_in_db(session):
    engine = create_engine('sqlite:///:memory:')
    mapper_registry.metadata.create_all(engine)
    new_user = User(user='user', email='email@email.com', password='password')
    session.add(user)
    session.commit()
    user = session.scalar(select(User).where(User.id == 1))
    assert user.id == 1
