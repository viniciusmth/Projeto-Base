from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import init_session
from backend.models import Todo, TodoState, User
from backend.schemas import TaskList, TodoPublic, TodoSchema, TodoUpdate
from backend.security import get_current_user

route = APIRouter(prefix='/todolist', tags=['to-do-list'])

t_get_current_user = Annotated[User, Depends(get_current_user)]
t_session = Annotated[Session, Depends(init_session)]


@route.post('/', response_model=TodoPublic)
def post_task(task: TodoSchema, current_user: t_get_current_user, session: t_session):
    task = Todo(title=task.title, description=task.description, state=task.state, user_id=current_user.id)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@route.get('/', response_model=TaskList)
def get_tasks(session: t_session, current_user: t_get_current_user, title: str | None = None, description: str | None = None, state: TodoState | None = None, limit: int | None = None, offset: int | None = None):
    query = select(Todo).where(Todo.user_id == current_user.id)
    if title:
        query = query.filter(Todo.title.contains(title))
    if description:
        query = query.filter(Todo.description.contains(description))
    if state:
        query = query.filter(Todo.state == state)
    if limit:
        query = query.limit(limit)
    if offset:
        query = query.offset(offset)

    tasks = session.scalars(query)
    return {'tasks': tasks}


@route.delete('/{task_id}', response_model=TodoPublic)
def delete_task(task_id: int, session: t_session, current_user: t_get_current_user):
    query = session.scalar(select(Todo).where(Todo.id == task_id, Todo.user_id == current_user.id))
    if not query:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="TASK DON'T EXISTS")
    session.delete(query)
    session.commit()
    return query


@route.patch('/{task_id}', response_model=TodoPublic)
def patch_task(task_id: int, current_user: t_get_current_user, session: t_session, todo: TodoUpdate):
    db_todo = session.scalar(select(Todo).where(Todo.id == task_id, Todo.user_id == current_user.id))
    if not db_todo:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="TASK DON'T EXISTS")
    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)
    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)
    return db_todo
