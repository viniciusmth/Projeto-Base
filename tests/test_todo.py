from http import HTTPStatus


def test_create_todo(client, token):
    response = client.post('/todolist', headers={'Authorization': f'Bearer {token}'}, json={'title': 'Estudar', 'description': 'Desenvolvimento Backend', 'state': 'draft'})
    assert response.status_code == HTTPStatus.OK
