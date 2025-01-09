from fastapi import FastAPI

from .routes import auth, users

app = FastAPI()
app.include_router(users.route)
app.include_router(auth.route)
