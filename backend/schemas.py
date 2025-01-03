from pydantic import BaseModel, EmailStr


class Message(BaseModel):
    message: str


class User(BaseModel):
    user: str
    email: EmailStr
    password: str


class UserID(User):
    id: int


class UserPublic(BaseModel):
    id: int
    user: str
    email: EmailStr


class UserList(BaseModel):
    users: list[UserPublic]


class UserName(BaseModel):
    user: str
