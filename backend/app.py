from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jwt import decode
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import init_session
from backend.models import User
from backend.schemas import Message, Token, UserDB, UserList, UserName, UserPublic
from backend.security import SECRET_KEY, SECURITY_TYPE, create_access_token, get_current_user, hash_to_password, password_to_hash

app = FastAPI()


@app.get('/users/', response_model=UserList)
def get_database(session: Session = Depends(init_session)):
    list_of_users = session.scalars(select(User))
    return {'users': list_of_users}


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def register_user(user: UserDB, session=Depends(init_session)):
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


@app.put('/users/{user_id}', response_model=UserPublic)
def put_user(user_id: int, user: UserDB, session=Depends(init_session), current_user=Depends(get_current_user)):
    if user_id != current_user.id:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="it's not possible validate credentials")
    if not session.scalar(select(User).where((user.username == User.username) or (user.email == User.email))):  # se não houver username ou email (unicos) parecido no banco de dados
        current_user.username = user.username  # Executamos isso (ALTERAMOS APENAS O USUÁRIO IDENTIFICADO QUE FEZ A REQUISIÇÃO)
        current_user.email = user.email
        current_user.password = password_to_hash(user.password)
        session.commit()
        session.refresh(current_user)
    else:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='User or email already exists')
    return current_user


@app.delete('/users/{user_id}', status_code=HTTPStatus.OK, response_model=Message)
def delete_user(user_id: int, session=Depends(init_session), current_user=Depends(get_current_user)):
    if user_id != current_user.id:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="it's not possible validate credentials")
    session.delete(current_user)
    session.commit()
    return {'message': f'User {current_user.username} deleted!'}


@app.get('/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserName)
def get_user_name(user_id: int, session=Depends(init_session)):
    db_user = session.scalar(select(User).where(User.id == user_id))
    if db_user:
        return {'username': str(db_user.username)}
    else:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User doesn't exist")


@app.post('/token', response_model=Token)
def login_for_acess_token(form_data: OAuth2PasswordRequestForm = Depends(), session=Depends(init_session)):
    user = session.scalar(select(User).where(User.email == form_data.username))
    if not user or not hash_to_password(form_data.password, user.password):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Email or password are incorrects')
    token = create_access_token({'sub': user.email})
    get_expire = decode(token, SECRET_KEY, SECURITY_TYPE)
    return {'access_token': token, 'token_type': 'Bearer', 'expire': get_expire.get('exp')}
