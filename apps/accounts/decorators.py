# from functools import wraps
# from starlette.responses import RedirectResponse
# from fastapi import Request, Depends
# from setup.extensions import manager

# def login_required(f):
#     @wraps(f)
#     def decorated_function(current_user=Depends(manager), *args, **kwargs):
#         if not current_user.is_authenticated:
#             return redirect(url_for('accounts_router.login', next=request.url))
#         return f(*args, **kwargs)
#     return decorated_function

# def logout_required(f):
#     @wraps(f)
#     def decorated_function(current_user=Depends(manager), *args, **kwargs):
#         if current_user.is_authenticated:
#             flash("You must logout first!", {"heading": "Not allowed", "tag": "info"})
#             return redirect(session.get('current_path'))
#         return f(*args, **kwargs)
#     return decorated_function