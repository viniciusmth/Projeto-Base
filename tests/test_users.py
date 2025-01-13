from http import HTTPStatus

from backend.schemas import UserPublic


def test_get_user_that_doesnt_exist(client):
    response = client.get('/users/-1')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_get_username(client, user):
    response = client.get(f'/users/{user.id}')
    response.json() == {'user': f'{user.username}'}


def test_get_database(client):
    response = client.get('/users/')
    assert response.json() == {'users': []}


def test_get_database_with_user(client, user):
    user_public = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')
    assert response.json() == {'users': [user_public]}


def test_put_user_that_not_you(client, user, other_user, token):
    response = client.put(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': user.username,
            'email': user.email,
            'password': user.email,
        },
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'NOT AUTHORIZATION'}


def test_put_user(client, user, token):
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


def test_put_identic_user_that_is_you(client, user, token):
    response = client.put(f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}, data={'username': 'vini', 'email': 'vini@vini.com', 'password': '123'})
    user_public = UserPublic.model_validate(user).model_dump()
    response.status_code == HTTPStatus.OK
    response.json() == user_public


def test_put_identic_user(client, user, other_user, token):
    response = client.put(f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}, json={'username': other_user.username, 'email': other_user.email, 'password': user.password})
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'User or email already exists'}


def test_delete_user_that_not_you(client, other_user, token):
    response = client.delete(f'/users/{other_user.id}', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'NOT AUTHORIZATION'}


def test_delete_user(client, user, token):
    response = client.delete(f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': f'User {user.username} deleted!'}


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


def test_create_user_that_exists(client, user):
    response = client.post(
        '/users/',
        json={
            'username': user.username,
            'email': user.email,
            'password': '123',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'USER OR EMAIL ALREADY EXISTS'}
