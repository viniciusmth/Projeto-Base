from fastapi import FastAPI

from .routes import auth, todolist, users

app = FastAPI()
app.include_router(users.route)
app.include_router(auth.route)
app.include_router(todolist.route)
