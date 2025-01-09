from http import HTTPStatus


def test_autenticate_user(client, user):
    response = client.post('/auth/token/', data={'username': user.email, 'password': user.clean_password})
    token = response.json()
    assert response.status_code == HTTPStatus.OK
    assert token['access_token']
    assert token['token_type'] == 'Bearer'
