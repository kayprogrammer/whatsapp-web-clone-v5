from typing import Union
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware import Middleware
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError
from starlette.middleware.sessions import SessionMiddleware
from sqladmin import Admin
from pydantic import BaseModel

from . database import engine, SQLALCHAMY_DATABASE_URL, Base
from . settings import *
from . extensions import *

from apps.accounts.views import accountsrouter
from apps.accounts.exceptions import NotAuthenticatedException
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
from apps.accounts import admin as accounts_admin
from apps.chat import admin as chat_admin

@app.exception_handler(NotAuthenticatedException)
def auth_exception_handler(request: Request, exc: NotAuthenticatedException):
    """
    Redirect the user to the login page if not logged in
    """
    response = RedirectResponse(request.url_for('login'))
    response.delete_cookie("access_token")
    return response

class CsrfSettings(BaseModel):
  secret_key:str = SECRET_KEY

@CsrfProtect.load_config
def get_csrf_config():
  return CsrfSettings()

@app.exception_handler(CsrfProtectError)
def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
    return JSONResponse(
    status_code=exc.status_code,
      content={ 'detail':  exc.message
    }
  )

@app.get('/')
def index(request: Request):
  return RedirectResponse(request.url_for('home'))