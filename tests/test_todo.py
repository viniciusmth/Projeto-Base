from http import HTTPStatus

from backend.schemas import TodoPublic
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


def test_get_todo_using_parameters(client, user, token, session):
    objects = TodoFactory.create_batch(5, user_id=user.id)
    for obj in objects:
        session.add(obj)
        session.commit()
        session.refresh(obj)
        sct_obj = obj
    sct_obj_to_public = TodoPublic.model_validate(sct_obj).model_dump()
    response = client.get(f'/todolist/?title={sct_obj.title}&description={sct_obj.description}&state={sct_obj.state}&limit=10', headers={'Authorization': f'Bearer {token}'})
    assert response.json() == {'tasks': [sct_obj_to_public]}


def test_get_todo_using_offset(client, user, token, session):
    objects = TodoFactory.create_batch(5, user_id=user.id)
    session.bulk_save_objects(objects)
    session.commit()
    response = client.get('/todolist/?offset=1', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.OK


def test_delete_todo(client, todo, token):
    response = client.delete(f'/todolist/{todo.id}', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.OK


def test_delete_todo_error(client, token):
    response = client.delete(f'/todolist/{9830}', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': "YOU DON'T HAVE PERMISSION FOR THIS"}
