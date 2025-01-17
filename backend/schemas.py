from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from backend.models import TodoState


class Message(BaseModel):
    message: str


class UserDB(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    users: list[UserPublic]


class UserName(BaseModel):
    username: str


class Token(BaseModel):
    access_token: str
    token_type: str
    expire: datetime


class TodoSchema(BaseModel):
    title: str
    description: str
    state: TodoState


class TodoPublic(TodoSchema):
    user_id: int
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TaskList(BaseModel):
    tasks: list[TodoPublic]


class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    state: TodoState | None = None
