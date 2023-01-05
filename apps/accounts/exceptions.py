from fastapi import HTTPException

class NotAuthenticatedException(HTTPException):
    pass