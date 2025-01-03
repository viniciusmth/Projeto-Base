from http import HTTPStatus

from fastapi import FastAPI, HTTPException

from backend.schemas import Message, User, UserID, UserList, UserName, UserPublic

app = FastAPI()

database = []


@app.get('/', response_model=Message)
def get_message():
    return {'message': 'oi, eu sou o chapeleiro'}


@app.get('/users/', response_model=UserList)
def get_database():
    return {'users': database}


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def register_user(user: User):
    user_with_id = UserID(id=len(database) + 1, **user.model_dump())

    database.append(user_with_id)

    return user_with_id


@app.put('/users/{user_id}', response_model=UserPublic)
def put_user(user_id: int, user: User):
    if user_id < 0 or user_id > len(database):
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Usuário não encontrado')
    new_user = UserID(**user.model_dump(), id=user_id)
    database[user_id - 1] = new_user
    return new_user


@app.delete('/users/{user_id}', status_code=HTTPStatus.OK, response_model=Message)
def delete_user(user_id: int):
    if user_id < 0 or user_id > len(database):
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Usuário não encontrado')

    del database[user_id - 1]
    return {'message': f'Usuário {user_id} deletado!'}


@app.get('/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserName)
def get_user_name(user_id: int):
    if user_id < 0 or user_id > len(database):
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Usuário não encontrado')
    user_name = database[user_id - 1].user
    return {'user': user_name}
