from starlette.responses import RedirectResponse
from fastapi import Request
import functools
import asyncio

def logout_required(func):
    @functools.wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        # Check if access token in header
        if request.cookies.get("access_token"):
            return RedirectResponse(request.url_for('home'))
        result = func(request, *args, **kwargs)
        if asyncio.iscoroutine(result):
            return await result
        return result
    return wrapper