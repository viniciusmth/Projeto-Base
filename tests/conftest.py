import factory
import factory.fuzzy
import pytest
from factory.faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from testcontainers.postgres import PostgresContainer

from backend.app import app
from backend.database import init_session
from backend.models import Todo, TodoState, User, mapper_registry
from backend.security import password_to_hash


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user_{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.LazyAttribute(lambda obj: password_to_hash(f'{obj.username}_password'))


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = Faker('name')
    description = Faker('name')
    state: str = factory.fuzzy.FuzzyChoice(TodoState)
    user_id: int
    id: int


@pytest.fixture
def client(session):
    def init_test_session():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[init_session] = init_test_session
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope='session')
def engine():
    with PostgresContainer('postgres:latest', driver='psycopg') as postgres:
        _engine = create_engine(postgres.get_connection_url())
        with _engine.begin():
            yield _engine


@pytest.fixture
def session(engine):
    mapper_registry.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    mapper_registry.metadata.drop_all(engine)


@pytest.fixture
def user(session):
    user = UserFactory()
    session.add(user)
    session.commit()
    session.refresh(user)
    pwd = f'{user.username}_password'
    user.clean_password = pwd
    return user


@pytest.fixture
def other_user(session):
    user = UserFactory()
    session.add(user)
    session.commit()
    session.refresh(user)
    pwd = f'{user.username}_password'
    user.clean_password = pwd
    return user


@pytest.fixture
def token(client, user):
    request = client.post('/auth/token', data={'username': user.email, 'password': user.clean_password})
    user_token = request.json()['access_token']
    return user_token


@pytest.fixture
def todo(session, user):
    task = TodoFactory(user_id=user.id)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
