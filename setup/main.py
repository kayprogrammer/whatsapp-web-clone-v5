from typing import Union
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from sqladmin import Admin

from . database import engine, SQLALCHAMY_DATABASE_URL, Base
from . settings import *

from apps.accounts.views import accountsrouter
from apps.chat.views import chatrouter
from apps.status.views import statusrouter

middleware = [
 Middleware(SessionMiddleware, secret_key=SECRET_KEY)
]

app = FastAPI(middleware = middleware)

Base.metadata.create_all(bind=engine)

admin = Admin(app, engine)

app.include_router(accountsrouter, prefix='/accounts')
app.include_router(chatrouter, prefix='/chat')
app.include_router(statusrouter, prefix='/status')

app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize admin models
from apps.accounts import admin