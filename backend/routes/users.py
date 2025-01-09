from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import User
from ..schemas import Message, UserDB, UserList, UserName, UserPublic
from ..security import get_current_user, init_session, password_to_hash

route = APIRouter(prefix='/users', tags=['users'])
T_Session = Annotated[Session, Depends(init_session)]
T_Current_User = Annotated[User, Depends(get_current_user)]


@route.get('/', response_model=UserList)
def get_database(session: T_Session):
    list_of_users = session.scalars(select(User))
    return {'users': list_of_users}


@route.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def register_user(user: UserDB, session: T_Session):
    db_user = session.scalar(select(User).where((user.username == User.username) or (user.email == User.email)))  # Verificamos se existe um usuário com as mesmas credenciais existes no banco de dados
    if db_user:  # Se existir
        if db_user.username == user.username:  # Se o usuario que foi encontrado possui username igual
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='User already exists')
        elif db_user.email == user.email:  # Ou se o usuário encontrado possui email igual
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Email already exists')
    db_user = User(username=user.username, email=user.email, password=password_to_hash(user.password))  # Se não existir, criamos um user novo, com as credenciais fornecidas
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@route.put('/{user_id}', response_model=UserPublic)
def put_user(user_id: int, user: UserDB, session: T_Session, current_user: T_Current_User):
    if user_id != current_user.id:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="it's not possible validate credentials")
    identic_user = session.scalar(select(User).where((user.username == User.username) or (user.email == User.email)))
    if identic_user:
        if identic_user.id == current_user.id:
            current_user.username = user.username
            current_user.email = user.email
            current_user.password = password_to_hash(user.password)
            session.commit()
            session.refresh(current_user)
        else:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='User or email already exists')
    else:
        current_user.username = user.username
        current_user.email = user.email
        current_user.password = password_to_hash(user.password)
        session.commit()
        session.refresh(current_user)
    return current_user


@route.delete('/{user_id}', status_code=HTTPStatus.OK, response_model=Message)
def delete_user(user_id: int, session: T_Session, current_user: T_Current_User):
    if user_id != current_user.id:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="it's not possible validate credentials")
    session.delete(current_user)
    session.commit()
    return {'message': f'User {current_user.username} deleted!'}


@route.get('/{user_id}', status_code=HTTPStatus.OK, response_model=UserName)
def get_user_name(user_id: int, session: T_Session):
    db_user = session.scalar(select(User).where(User.id == user_id))
    if db_user:
        return {'username': str(db_user.username)}
    else:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User doesn't exist")
