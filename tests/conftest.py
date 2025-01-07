import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from backend.app import app
from backend.database import init_session
from backend.models import User, mapper_registry
from backend.security import password_to_hash


@pytest.fixture
def client(session):
    def init_test_session():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[init_session] = init_test_session
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def session():
    engine = create_engine('sqlite:///:memory:', poolclass=StaticPool, connect_args={'check_same_thread': False})
    mapper_registry.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    mapper_registry.metadata.drop_all(engine)


@pytest.fixture
def user(session):
    pwd = '123'
    user = User(username='vini', email='vini@vini.com', password=password_to_hash(pwd))
    session.add(user)
    session.commit()
    session.refresh(user)
    user.clean_password = pwd
    return user
