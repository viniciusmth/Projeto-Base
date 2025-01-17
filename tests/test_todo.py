from http import HTTPStatus

from tests.conftest import TodoFactory


def test_create_todo(client, token):
    response = client.post('/todolist', headers={'Authorization': f'Bearer {token}'}, json={'title': 'Estudar', 'description': 'Desenvolvimento Backend', 'state': 'draft'})
    assert response.status_code == HTTPStatus.OK


def test_create_various_todos(client, user, token, session):
    session.bulk_save_objects(TodoFactory.create_batch(5, user_id=user.id))
    session.commit()
    response = client.get('/todolist/', headers={'Authorization': f'Bearer {token}'})
    expected_value_of_objects = 5
    assert len(response.json()['tasks']) == expected_value_of_objects


def test_get_todo_using_parameters(client, token, todo):
    response = client.get(f'/todolist/?title={todo.title}&description={todo.description}&state={todo.state.value}&limit=10', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.OK


def test_get_todo_using_offset(client, user, token, session):
    objects = TodoFactory.create_batch(2, user_id=user.id)
    session.bulk_save_objects(objects)
    session.commit()
    response = client.get('/todolist/?offset=1', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.OK


def test_delete_todo(client, todo, token):
    response = client.delete(f'/todolist/{todo.id}', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.OK


def test_delete_todo_error(client, token):
    response = client.delete(f'/todolist/{10}', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': "TASK DON'T EXISTS"}


def test_patch_todo(client, token, todo):
    response = client.patch(f'/todolist/{todo.id}', headers={'Authorization': f'Bearer {token}'}, json={'title': 'TREINAR'})
    assert response.status_code == HTTPStatus.OK


def test_patch_todo_error(client, token):
    response = client.patch(f'/todolist/{10}', headers={'Authorization': f'Bearer {token}'}, json={'title': 'TREINAR'})
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': "TASK DON'T EXISTS"}
