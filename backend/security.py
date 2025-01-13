from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import ExpiredSignatureError, PyJWTError, decode, encode
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import init_session
from backend.models import User
from backend.settings import Settings

context = PasswordHash.recommended()

oauth_authorization = OAuth2PasswordBearer(tokenUrl='auth/token')
SECRET_KEY = Settings().SECRET_KEY
SECURITY_TYPE = Settings().SECURITY_TYPE
TIME_FOR_EXPIRE_TOKEN = Settings().TIME_FOR_EXPIRE_TOKEN

t_session = Annotated[Session, Depends(init_session)]
t_current_user = Annotated[str, Depends(oauth_authorization)]
credential_exception = HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="COULD'T VALIDATE CREDENTIALS", headers={'WWW-Authenticate': 'Bearer'})


def password_to_hash(password: str):
    return context.hash(password)


def hash_to_password(clear_password: str, hashed_password: str):
    return context.verify(clear_password, hashed_password)


def create_access_token(data_payload: dict):
    date_for_expire = datetime.now(tz=timezone.utc) + timedelta(minutes=TIME_FOR_EXPIRE_TOKEN)
    data_payload.update({'exp': date_for_expire})
    token_encoded = encode(data_payload, SECRET_KEY, SECURITY_TYPE)
    return token_encoded


def get_current_user(session: t_session, current_user: t_current_user):
    try:
        user_authorized = decode(current_user, SECRET_KEY, [SECURITY_TYPE])
        user_email = user_authorized.get('sub')
    except ExpiredSignatureError:
        raise ExpiredSignatureError
    except PyJWTError:
        raise PyJWTError
    user_db = session.scalar(select(User).where(User.email == user_email))
    if not user_db:
        raise credential_exception
    return user_db
