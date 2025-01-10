from http import HTTPStatus

from backend.schemas import UserPublic


def test_get_user_that_doesnt_exist(client):
    response = client.get('/users/-1')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_get_username(client, user):
    p_user = user[0]
    response = client.get(f'/users/{p_user.id}')
    response.json() == {'user': f'{p_user.username}'}


def test_get_database(client):
    response = client.get('/users/')
    assert response.json() == {'users': []}


def test_get_database_with_user(client, user):
    user_public = []
    for i in user:
        user_public.append(UserPublic.model_validate(i).model_dump())
    response = client.get('/users/')
    assert response.json() == {'users': user_public}


def test_put_user_that_not_you(client, user, token):
    p_user = user[0]
    response = client.put(
        f'/users/{p_user.id + 1}',
        headers={'Authorization': f'Bearer {token[0]}'},
        json={
            'username': 'vinicius',
            'email': 'email@email.com',
            'password': 'vinicius',
        },
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'NOT AUTHORIZATION'}


def test_put_user(client, user, token):
    p_user = user[0]
    response = client.put(
        f'/users/{p_user.id}',
        headers={'Authorization': f'Bearer {token[0]}'},
        json={
            'username': 'felipe',
            'email': 'email2@email.com',
            'password': '123',
        },
    )
    user_public = UserPublic.model_validate(p_user).model_dump()
    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_public


def test_put_identic_user_that_is_you(client, user, token):
    p_user = user[0]
    p_token = token[0]
    response = client.put(f'/users/{p_user.id}', headers={'Authorization': f'Bearer {p_token}'}, data={'username': 'vini', 'email': 'vini@vini.com', 'password': '123'})
    user_public = UserPublic.model_validate(p_user).model_dump()
    response.status_code == HTTPStatus.OK
    response.json() == user_public


def test_put_identic_user(client, user, token):
    p_user = user[0]
    s_user = user[1]
    response = client.put(f'/users/{p_user.id}', headers={'Authorization': f'Bearer {token[0]}'}, json={'username': s_user.username, 'email': s_user.email, 'password': s_user.password})
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'User or email already exists'}


def test_delete_user_that_not_you(client, user, token):
    p_user = user[0]
    response = client.delete(f'/users/{p_user.id + 1}', headers={'Authorization': f'Bearer {token[0]}'})
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'NOT AUTHORIZATION'}


def test_delete_user(client, user, token):
    p_user = user[0]
    response = client.delete(f'/users/{p_user.id}', headers={'Authorization': f'Bearer {token[0]}'})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': f'User {p_user.username} deleted!'}


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
            'username': 'vini',
            'email': 'vini@vini.com',
            'password': '123',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'USER OR EMAIL ALREADY EXISTS'}
