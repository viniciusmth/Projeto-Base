from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jwt import decode
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import init_session
from ..models import User
from ..schemas import Token
from ..security import SECRET_KEY, SECURITY_TYPE, create_access_token, hash_to_password

route = APIRouter(prefix='/auth', tags=['auth'])
T_Session = Annotated[Session, Depends(init_session)]
T_Form = Annotated[OAuth2PasswordRequestForm, Depends()]


@route.post('/token', response_model=Token)
def login_for_access_token(form_data: T_Form, session: T_Session):
    user = session.scalar(select(User).where(User.email == form_data.username))
    if not user or not hash_to_password(form_data.password, user.password):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Email or password are incorrects')
    token = create_access_token({'sub': user.email})
    get_expire = decode(token, SECRET_KEY, SECURITY_TYPE)
    return {'access_token': token, 'token_type': 'Bearer', 'expire': get_expire.get('exp')}
