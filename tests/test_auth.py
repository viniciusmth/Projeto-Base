from http import HTTPStatus

import pytest
from fastapi import HTTPException
from freezegun import freeze_time
from jwt import PyJWTError
from jwt.exceptions import ExpiredSignatureError

from backend.security import create_access_token, get_current_user


def test_autenticate_user(client, user):
    response = client.post('/auth/token/', data={'username': user.email, 'password': user.clean_password})
    token = response.json()
    assert response.status_code == HTTPStatus.OK
    assert token['access_token']
    assert token['token_type'] == 'Bearer'


def test_login_user_that_email_not_exist(client):
    response = client.post('/auth/token', data={'username': 'not@exist.com', 'password': 'not_exist'})
    assert response.json() == {'detail': 'EMAIL ARE INCORRECT'}
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_login_user_that_password_not_exist(client, user):
    response = client.post('/auth/token', data={'username': user.email, 'password': 'not_exist'})
    assert response.json() == {'detail': 'PASSWORD ARE INCORRECT'}
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_get_current_user_with_invalid_token(client):
    response = client.delete(
        '/auth/token/1',
        headers={'Authorization': 'Bearer invalid-token'},
    )
    response.status_code == HTTPStatus.UNAUTHORIZED
    response.json() == {'detail': "COULD'T VALIDATE CREDENTIALS"}


def test_get_current_user_jwt_error(session):
    with pytest.raises(PyJWTError):
        get_current_user(session=session, current_user='invalid_token')


def test_get_current_user_that_email_not_exists_in_db(session):
    token = create_access_token({'sub': 'oi@email.com'})
    with pytest.raises(HTTPException):
        get_current_user(session=session, current_user=token)


def test_expired_token(client, user):
    with freeze_time('2023-07-14 12:00:00'):
        response = client.post('/auth/token', data={'username': user.email, 'password': user.clean_password})
        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']
    with freeze_time('2023-07-14 12:31:00'):
        with pytest.raises(ExpiredSignatureError):
            response = client.put(f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}, json={'username': user.username, 'email': user.email, 'password': user.clean_password})


def test_refresh_token(client, token):
    response = client.post('/auth/refresh_token', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.OK
    assert response.json()['access_token']
