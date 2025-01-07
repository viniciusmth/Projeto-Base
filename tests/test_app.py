from http import HTTPStatus

from backend.schemas import UserPublic


def test_get_database(client):
    response = client.get('/users/')
    assert response.json() == {'users': []}


def test_get_database_with_user(client, user):
    user_public = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')
    assert response.json() == {'users': [user_public]}


def test_put_user_that_doesnt_exist(client, user):
    response = client.put(
        '/users/-1',
        json={
            'username': 'vinicius',
            'email': 'email@email.com',
            'password': 'vinicius',
        },
    )
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_user_that_doesnt_exist(client):
    response = client.delete('/users/-1')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_get_user_that_doesnt_exist(client):
    response = client.get('/users/-1')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_create_user(client):
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


def test_create_user_that_exists_user(client, user):
    response = client.post(
        '/users/',
        json={
            'username': 'vini',
            'email': 'vini@email.com',
            'password': '123',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Usuário já cadastrado'}


def test_create_user_that_exists_email(client, user):
    response = client.post(
        '/users/',
        json={
            'username': 'jorel',
            'email': 'vini@vini.com',
            'password': '123',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Email já cadastrado'}


def test_put_user(client, user):
    response = client.put(
        f'/users/{user.id}',
        json={
            'username': 'felipe',
            'email': 'email2@email.com',
            'password': '123',
        },
    )
    user_public = UserPublic.model_validate(user).model_dump()
    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_public


def test_get_username(client, user):
    response = client.get(f'/users/{user.id}')
    response.json() == {'user': f'{user.username}'}


def test_delete_user(client, user):
    response = client.delete(f'/users/{user.id}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': f'User {user.username} deleted!'}
