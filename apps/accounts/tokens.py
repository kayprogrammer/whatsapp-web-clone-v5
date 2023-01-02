from datetime import datetime, timedelta
import jwt
from setup.settings import SECRET_KEY
from . models import User

class Token:
    def get_activation_token(user, db):
        token = jwt.encode({'activate_user': str(user.id), 'exp':datetime.utcnow() + timedelta(seconds=900)}, key=SECRET_KEY, algorithm="HS256") 
        user.current_activation_jwt = {'token': token, 'used': False }
        db.commit()
        return token

    def verify_activation_token(token):
        try:
            user_id = jwt.decode(token,
              key=SECRET_KEY, algorithms=["HS256"])['activate_user']

            user = User.query.filter_by(id=user_id).first()
        except Exception as e:
            return None
        
        if not user:
            return None

        if token != user.current_activation_jwt.get('token'): # Just to invalidate old tokens that are yet to expire
            return None

        if user.current_activation_jwt.get('used') == True:
            return None
        return user

    def get_reset_token(user, db):
        token = jwt.encode({'reset_password': str(user.id),
                           'exp': datetime.utcnow() + timedelta(seconds=900)},
                           key=SECRET_KEY, algorithm="HS256")
        user.current_password_jwt = {'token': token, 'used': False }

        db.commit()
        return token

    def verify_reset_token(token, db):
        try:
            user_id = jwt.decode(token,
              key=SECRET_KEY, algorithms=["HS256"])['reset_password']

            user = User.query.filter_by(id=user_id).first()
        except Exception as e:
            return None

        if not user:
            return None

        if token != user.current_password_jwt.get('token'): # Just to invalidate old tokens that are yet to expire
            return None

        if user.current_password_jwt.get('used') == True:
            return None

        user.current_password_jwt['used'] = True
        db.commit()
        return user