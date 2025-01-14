from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import init_session
from backend.models import Todo, User
from backend.schemas import TodoPublic, TodoSchema
from backend.security import get_current_user

route = APIRouter(prefix='/todolist', tags=['to-do-list'])

t_get_current_user = Annotated[User, Depends(get_current_user)]
t_session = Annotated[Session, Depends(init_session)]


@route.post('', response_model=TodoPublic)
def post_task(task: TodoSchema, current_user: t_get_current_user, session: t_session):
    task = Todo(title=task.title, description=task.description, state=task.state, user_id=current_user.id)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
