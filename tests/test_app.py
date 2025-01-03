from http import HTTPStatus


def test_get_message(client):
    response = client.get('/')
    assert response.json() == {'message': 'oi, eu sou o chapeleiro'}


def test_get_database(client):
    response = client.get('/users/')
    assert response.json() == {'users': []}


def test_put_user_that_doesnt_exist(client):
    response = client.put(
        '/users/-1',
        json={
            'user': 'vinicius',
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
            'user': 'vinicius',
            'email': 'email@email.com',
            'password': 'vinicius',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'user': 'vinicius',
        'email': 'email@email.com',
        'id': 1,
    }


def test_put_user(client):
    response = client.put(
        '/users/1',
        json={
            'user': 'felipe',
            'email': 'email2@email.com',
            'password': '123',
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'user': 'felipe',
        'email': 'email2@email.com',
    }


def test_get_username(client):
    response = client.get('/users/1')
    response.json() == {'user': 'felipe'}


def test_delete_user(client):
    delete_user = 1
    response = client.delete(f'/users/{delete_user}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': f'Usuário {delete_user} deletado!'}
