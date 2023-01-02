from fastapi import Request
from fastapi_login import LoginManager


from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . settings import SECRET_KEY

import typing

manager = LoginManager(SECRET_KEY, '/accounts/login/', use_cookie=True)

manager.cookie_name = 'user_session'

def flash(request: Request, message: typing.Any, category: str = "primary") -> None:
   if "_messages" not in request.session:
       request.session["_messages"] = []
       request.session["_messages"].append({"message": message, "category": category})
def get_flashed_messages(request: Request):
   return request.session.pop("_messages") if "_messages" in request.session else []
