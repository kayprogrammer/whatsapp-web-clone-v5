from fastapi import Request

from starlette.applications import Starlette
from starlette.authentication import (
    AuthCredentials, AuthenticationBackend, AuthenticationError, SimpleUser
)
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.responses import PlainTextResponse
from starlette.routing import Route
import base64
import binascii
import typing

# class BasicAuthBackend(AuthenticationBackend):
#     async def authenticate(self, conn):
#         if "Authorization" not in conn.headers:
#             return

#         auth = conn.headers["Authorization"]
#         try:
#             scheme, credentials = auth.split()
#             if scheme.lower() != 'basic':
#                 return
#             decoded = base64.b64decode(credentials).decode("ascii")
#         except (ValueError, UnicodeDecodeError, binascii.Error) as exc:
#             raise AuthenticationError('Invalid basic auth credentials')

#         username, _, password = decoded.partition(":")
#         # TODO: You'd want to verify the username and password here.
#         return AuthCredentials(["authenticated"]), SimpleUser(username)


# async def homepage(request):
#     if request.user.is_authenticated:
#         return PlainTextResponse('Hello, ' + request.user.display_name)
#     return PlainTextResponse('Hello, you')

# routes = [
#     Route("/", endpoint=homepage)
# ]

# middleware = [
#     Middleware(AuthenticationMiddleware, backend=BasicAuthBackend())
# ]

# app = Starlette(routes=routes, middleware=middleware)


# from werkzeug.wrappers import Request, Response, ResponseStream

# class middleware():
#     '''
#     Simple WSGI middleware
#     '''

#     def __init__(self, app):
#         self.app = app
#         self.userName = 'Tony'
#         self.password = 'IamIronMan'

#     def __call__(self, environ, start_response):
#         request = Request(environ)
#         timezone = request.authorization['username']
#         password = request.authorization['password']
        
#         # these are hardcoded for demonstration
#         # verify the username and password from some database or env config variable
#         if userName == self.userName and password == self.password:
#             environ['user'] = { 'name': 'Tony' }
#             return self.app(environ, start_response)

#         res = Response(u'Authorization failed', mimetype= 'text/plain', status=401)
#         return res(environ, start_response)
