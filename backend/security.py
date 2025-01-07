from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.database import init_session
from jwt import encode
from pwdlib import PasswordHash

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
    date_for_expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(minutes=TIME_FOR_EXPIRE_TOKEN)
    data_payload.update({'exp': date_for_expire})
    token_encoded = encode(data_payload, SECRET_KEY, SECURITY_TYPE)
    return token_encoded

def get_current_user(
        session: Session = Depends(init_session),
        is_logged: str = Depends(oauth_authorization)):
    return