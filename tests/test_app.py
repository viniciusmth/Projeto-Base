from http import HTTPStatus

from fastapi.testclient import TestClient

from backend.models import User
from backend.schemas import UserPublic


def test_get_database(client: TestClient):
    response = client.get('/users/')
    assert response.json() == {'users': []}


def test_get_database_with_user(client: TestClient, user: User):
    user_public = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')
    assert response.json() == {'users': [user_public]}


def test_put_user_that_doesnt_exist(client: TestClient, user: User, token):
    response = client.put(
        '/users/-1',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'vinicius',
            'email': 'email@email.com',
            'password': 'vinicius',
        },
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_delete_user_that_doesnt_exist(client: TestClient, token):
    response = client.delete('/users/-1', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_get_user_that_doesnt_exist(client: TestClient):
    response = client.get('/users/-1')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_create_user(client: TestClient):
    response = client.post(
        '/users/',
        json={
            'username': 'vini',
            'email': 'vini@vini.com',
            'password': '123',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'username': 'vini',
        'email': 'vini@vini.com',
        'id': 1,
    }


def test_create_user_that_exists_email(client: TestClient, user: User):
    response = client.post(
        '/users/',
        json={
            'username': 'jorel',
            'email': 'vini@vini.com',
            'password': '123',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Email already exists'}


def test_put_user(client: TestClient, user: User, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'felipe',
            'email': 'email2@email.com',
            'password': '123',
        },
    )
    user_public = UserPublic.model_validate(user).model_dump()
    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_public


def test_get_username(client: TestClient, user: User):
    response = client.get(f'/users/{user.id}')
    response.json() == {'user': f'{user.username}'}


def test_delete_user(client: TestClient, user: User, token):
    response = client.delete(f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': f'User {user.username} deleted!'}


def test_autenticate_user(client: TestClient, user: User):
    response = client.post('/token/', data={'username': user.email, 'password': user.clean_password})
    token = response.json()
    assert response.status_code == HTTPStatus.OK
    assert token['access_token']
    assert token['token_type'] == 'Bearer'
