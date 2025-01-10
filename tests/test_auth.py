from http import HTTPStatus


def test_autenticate_user(client, user):
    p_user = user[0]
    response = client.post('/auth/token/', data={'username': p_user.email, 'password': p_user.clean_password})
    token = response.json()
    assert response.status_code == HTTPStatus.OK
    assert token['access_token']
    assert token['token_type'] == 'Bearer'


def test_login_user_that_not_exists(client):
    response = client.post('/auth/token', data={'username': 'not@exist.com', 'password': 'not_exist'})
    assert response.json() == {'detail': 'EMAIL OR PASSWORD ARE INCORRECTS'}
    assert response.status_code == HTTPStatus.BAD_REQUEST
