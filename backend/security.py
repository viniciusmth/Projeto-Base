from datetime import datetime, timedelta, timezone
from http import HTTPStatus

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError, decode, encode
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import init_session
from backend.models import User

context = PasswordHash.recommended()

oauth_authorization = OAuth2PasswordBearer(tokenUrl='token')

SECRET_KEY = '123'
SECURITY_TYPE = 'HS256'
TIME_FOR_EXPIRE_TOKEN = 30


def password_to_hash(password: str):
    return context.hash(password)


def hash_to_password(clear_password: str, hashed_password: str):
    return context.verify(clear_password, hashed_password)


def create_access_token(data_payload: dict):
    date_for_expire = datetime.now(tz=timezone.utc) + timedelta(minutes=TIME_FOR_EXPIRE_TOKEN)
    data_payload.update({'exp': date_for_expire})
    token_encoded = encode(data_payload, SECRET_KEY, SECURITY_TYPE)
    return token_encoded


def get_current_user(session: Session = Depends(init_session), current_user: str = Depends(oauth_authorization)):
    credential_exception = HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Could't validate credentials", headers={'WWW-Authenticate': 'Bearer'})
    try:
        user_authorized = decode(current_user, SECRET_KEY, [SECURITY_TYPE])
        user_authorized_email = user_authorized.get('sub')
        if not user_authorized_email:
            raise credential_exception
    except PyJWTError:
        raise credential_exception
    user_db = session.scalar(select(User).where(User.email == user_authorized_email))
    if not user_db:
        raise credential_exception
    return user_db
