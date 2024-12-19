from http import HTTPStatus

from fastapi.testclient import TestClient

from backend.app import app


def test_():
    client = TestClient(app)
    response = client.get('/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'body': 'vinicius'}
