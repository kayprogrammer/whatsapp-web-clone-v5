from fastapi_mail import MessageSchema, FastMail, MessageType
from setup.settings import SITE_NAME, DEFAULT_FROM_PHONE, DEFAULT_FROM_EMAIL, email_conf
from . threads import SmsMessageThread
from . tokens import Token
import random
import jwt

class Util:
    @staticmethod
    async def send_verification_email(request, user, db):
        scheme = request.scope['scheme']
        host = request.headers['host']
        current_site = f'{scheme}://{host}'
        subject = 'Activate your account'
        msg = MessageSchema(
                subject=subject,
                recipients = [user.email],
                template_body={'request': request, 'name': user.name, 'domain': current_site, 'site_name': SITE_NAME, 'token': Token.get_activation_token(user, db), 'user_id': user.id, 'sender_email': DEFAULT_FROM_EMAIL},
                subtype=MessageType.html
            )

        fm = FastMail(email_conf)
        await fm.send_message(msg, template_name='email-activation-message.html')
    
    @staticmethod
    def send_sms_otp(user, db):
        code = random.randint(100000, 999999)
        from . models import Otp 
        otp = Otp.get_or_create(db=db, user_id=user.id)
        otp.value = code
        db.commit()
        body = f'Hello {user.name}! \nYour Phone Verification OTP from {SITE_NAME} is {code} \nExpires in 15 minutes',
        from_ = DEFAULT_FROM_PHONE,
        to = user.phone

        SmsMessageThread(body, from_, to).start()

    @staticmethod
    async def send_welcome_email(request, user):
        scheme = request.scope['scheme']
        host = request.headers['host']
        current_site = f'{scheme}://{host}'
        subject = 'Account Verified'
        msg = MessageSchema(
                subject=subject,
                recipients = [user.email],
                template_body={'name': user.name, 'domain': current_site, 'site_name': SITE_NAME},
                subtype=MessageType.html
            )
        
        fm = FastMail(email_conf)
        await fm.send_message(msg, template_name='welcomemessage.html')


    @staticmethod
    async def send_password_reset_email(request, user, db):
        current_site = f'{request.scheme}://{request.host}'
        subject = 'Reset your password'
        msg = Message(
                subject=subject,
                recipients = [user.email],
                template_body={'request': request, 'name': user.name, 'domain': current_site, 'site_name': SITE_NAME, 'token': Token.get_reset_token(user, db), 'user_id': user.id, 'sender_email': DEFAULT_FROM_EMAIL},
                subtype=MessageType.html
            )
        fm = FastMail(email_conf)
        await fm.send_message(msg, template_name='email-password-reset.html')
