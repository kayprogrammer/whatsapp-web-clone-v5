from fastapi import Request, APIRouter, Form, HTTPException, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from . forms import RegisterForm, LoginForm, OtpVerificationForm, PasswordResetRequestForm, PasswordResetForm
from . models import User, Timezone
from fastapi import Depends
from fastapi.templating import Jinja2Templates

from setup.database import get_db
from setup.extensions import get_flashed_messages, flash

from sqlalchemy import or_
from sqlalchemy.orm import Session
from . senders import Util
from . tokens import Token
from . utils import OAuth2PasswordBearerWithCookie
from . exceptions import NotAuthenticatedException
from pathlib import Path
import pytz

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "templates"
accountsrouter = APIRouter(tags=['accounts'])
templates = Jinja2Templates(directory=TEMPLATE_DIR)
templates.env.globals['get_flashed_messages'] = get_flashed_messages

# Get current user
oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl = "/accounts/login")
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = Token.decodeJWT(db, token) # check access token validity. returns user object or None
    if not user:
        raise NotAuthenticatedException(status_code = 401, detail='Signature invalid or expired')

    return user

@accountsrouter.api_route('/register/', methods=['GET', 'POST'])
async def register(backgroundtasks: BackgroundTasks, request: Request, response_class = HTMLResponse, db: Session = Depends(get_db)):
    form_data = await request.form()
    form = RegisterForm(form_data, db=db)
    timezones = db.query(Timezone).all()
    timezones_list=[(t.name, t.name) for t in timezones]
    form.tz.choices = timezones_list

    if request.method == 'POST' and form.validate():
        user = User.create_user(db=db,
            name=form.name.data,
            email=form.email.data.lower(),
            phone=form.phone.data,
            tz=form.tz.data,
            password=form.password.data,
            terms_agreement=form.terms_agreement.data,
        )
        Util.send_verification_email(backgroundtasks, request, user, db)
        return templates.TemplateResponse('accounts/email-activation-request.html', {'request': request, 'detail':'sent', 'email':user.email})
    print(form.errors)
    return templates.TemplateResponse('accounts/register.html', {'request': request, 'form': form})

@accountsrouter.api_route('/activate-user/{token}/{user_id}/', methods=['GET'])
def activate_user(backgroundtasks: BackgroundTasks, request: Request, token, user_id, response_class = HTMLResponse, db: Session = Depends(get_db)):
    user_obj = db.query(User).filter_by(id=user_id).first()
    if not user_obj:
        flash(request, "You entered an invalid link!", {"heading": "Invalid", "tag": "error"})
        return RedirectResponse(request.url_for("login"))
    user = Token.verify_activation_token(token, db)
    if not user:
        return templates.TemplateResponse('accounts/email-activation-failed.html', {'request': request, 'email':user_obj.email})
    if user.id != user_obj.id:
        flash(request, "You entered an invalid link!", {"heading": "Invalid", "tag": "error"})
        return RedirectResponse(request.url_for("login"))

    user.current_activation_jwt['used'] = True
    user.is_email_verified = True
    db.add(user)
    db.commit()
    db.refresh(user)

    if not user.is_phone_verified:
        Util.send_sms_otp(user, db)
        request.session['verification_phone'] = user.phone
        flash(request, "Activation successful!. Verify your phone now!", {"heading": "Done", "tag": "success"})
        return RedirectResponse(request.url_for('verify_otp'))

    flash(request, "Activation successful!.", {"heading": "Done", "tag": "success"})
    Util.send_welcome_email(backgroundtasks, request, user)
    return RedirectResponse(request.url_for("login"))

@accountsrouter.api_route('/resend-activation-email/', methods=['GET'])
def resend_activation_email(backgroundtasks: BackgroundTasks, request: Request, response_class = HTMLResponse, db: Session = Depends(get_db)):
    email = request.cookies.get('activation_email')
    user_obj = User.query.filter_by(email=email).first()
    if not user_obj:
        flash(request, "Something went wrong!.", {"heading": "error", "tag": "error"})
        return RedirectResponse(request.url_for("login"))
    if user_obj.is_email_verified:
        flash(request, "Your email address has already been verified!.", {"heading": "Verified", "tag": "info"})
        return RedirectResponse(request.url_for("login"))

    Util.send_verification_email(backgroundtasks, request, user_obj, db)
    return templates.TemplateResponse('accounts/email-activation-request.html', {'request': request, 'detail':'resent', 'email':email})

@accountsrouter.api_route('/verify-otp', methods=['GET', 'POST'])
async def verify_otp(background_tasks: BackgroundTasks, request: Request, response_class = HTMLResponse, db: Session = Depends(get_db)):
    form_data = await request.form()
    phone = request.session.get('verification_phone')
    if not phone:
        flash(request, "Back to login!.", {"heading": "Error!", "tag": "error"})
        return RedirectResponse(request.url_for('login'))
    form = OtpVerificationForm(form_data, request=request, db=db, background_tasks=background_tasks)
    if request.method == 'POST' and form.validate():
        flash(request, "You can login now.", {"heading": "Verification complete!", "tag": "success"})
        return RedirectResponse(request.url_for('login'))
    return templates.TemplateResponse('accounts/otp-verification.html', {'request':request, 'form': form})

@accountsrouter.api_route('/resend-otp', methods=['GET'])
def resend_otp(request: Request, db: Session = Depends(get_db)):
    phone = request.session.get('verification_phone')
    if not phone:
        flash(request, "Something went wrong.", {"heading": "Error!", "tag": "info"})
        return RedirectResponse(request.url_for('login'))
    user = db.query(User).filter_by(phone=phone).first()
    if not user:
        flash(request, "Invalid user.", {"heading": "Error!", "tag": "error"})
        return RedirectResponse(request.url_for('login'))
    if user.is_phone_verified:
        flash(request, "Your phone number has already been verified.", {"heading": "Already verified!", "tag": "info"})
        return RedirectResponse(request.url_for('login'))
    
    Util.send_sms_otp(user, db)
    flash(request, "A new otp has been sent to your phone number.", {"heading": "Sent!", "tag": "success"})
    return RedirectResponse(request.url_for('verify_otp'))


@accountsrouter.api_route('/login', methods=['GET', 'POST'])
async def login(backgroundtasks: BackgroundTasks, request: Request, response_class = HTMLResponse, db: Session = Depends(get_db)):
    request.session['password_reset_email'] = None
    form_data = await request.form()

    form = LoginForm(form_data)
    if request.method == 'POST' and form.validate():
        user = db.query(User).filter(or_(User.email==form.email_or_phone.data, User.phone==form.email_or_phone.data)).first()
        if not user:
            flash(request, "Invalid credentials.", {"heading": "Error!", "tag": "error"})
            return templates.TemplateResponse('accounts/login.html', {'request': request, 'form':form})
        password_check = user.check_password(form.password.data)
        if password_check == False:
            flash(request, "Invalid credentials.", {"heading": "Error!", "tag": "error"})
            return templates.TemplateResponse('accounts/login.html', {'request': request, 'form':form}) 
        print(user.is_phone_verified)
        if not user.is_email_verified:
            Util.send_verification_email(backgroundtasks, request, user, db)
            return templates.TemplateResponse('accounts/email-activation-request.html', {'request': request, 'detail': 'request', 'email': user.email})

        if not user.is_phone_verified:
            Util.send_sms_otp(user, db)
            request.session['verification_phone'] = user.phone
            return RedirectResponse(request.url_for('verify_otp'))
        response = RedirectResponse(request.url_for("home"))
        access_token = Token.get_access_token({"user_id": str(user.id)})
        response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
        return response
    return templates.TemplateResponse('accounts/login.html', {'request': request, 'form':form})

@accountsrouter.api_route('/logout', methods=['GET'], )
def logout(request: Request, user: User = Depends(get_current_user)):
    response = RedirectResponse(request.url_for('login'))
    response.delete_cookie("access_token")
    return response

@accountsrouter.api_route('/request-password-reset', methods=['GET', 'POST'])
def password_reset_request(backgroundtasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    detail = 'first_view'
    form = PasswordResetRequestForm(request.form)
    if form.validate_on_submit():
        user = db.query(User).filter_by(email=form.email.data).first()
        if user:
            Util.send_password_reset_email(backgroundtasks, request, user, db)
            request.session['password_reset_email'] = user.email
            detail = 'second_view'
    return templates.TemplateResponse('accounts/password-reset-request.html', detail=detail, form=form)

@accountsrouter.api_route('/verify-password-reset-token/<token>/<user_id>', methods=['GET', 'POST'])
def verify_password_reset_token(request: Request, token, user_id, db: Session = Depends(get_db)):
    detail = 'invalid_token'
    form = None
    try:
        user_obj = db.query(User).filter_by(id=user_id).first()
    except:
        flash(request, "You entered an invalid link.", {"heading": "Error!", "tag": "error"})
        return RedirectResponse(request.url_for("login"))
    user = Token.verify_reset_token(token, db)
    
    if user and user.id != user_obj.id:
        flash(request, "You entered an invalid link.", {"heading": "Error!", "tag": "error"})
        return RedirectResponse(request.url_for("login"))
    elif user and user.id == user_obj.id:
        request.session['password_reset_email'] = user_obj.email
        return RedirectResponse(request.url_for('reset_password'))
    return templates.TemplateResponse('accounts/password-reset.html', detail=detail, form=form, email=user_obj.email)

@accountsrouter.api_route('/reset-password', methods=['GET', 'POST'])
def reset_password(request: Request, db: Session = Depends(get_db)):
    email=request.session.get('password_reset_email')
    user = db.query(User).filter_by(email=email).first()
    if not user:
        flash(request, "Not allowed.", {"heading": "Error!", "tag": "error"})
        return RedirectResponse(request.url_for('login'))
    detail = 'valid_token'
    form = PasswordResetForm(request.form)
    if form.validate_on_submit():
        if user:
            user.password = form.newpassword.data
            db.add(user)
            db.commit()
            db.refresh(user)
            flash(request, "Your password has been reset.", {"heading": "Success!", "tag": "success"})
            request.session['password_reset_email'] = None
            return RedirectResponse(request.url_for("login"))
    return templates.TemplateResponse('accounts/password-reset.html', detail=detail, form=form, email=email)

@accountsrouter.api_route('/resend-password-token/<email>', methods=['GET'])
async def resend_password_token(backgroundtasks: BackgroundTasks, request: Request, email, db: Session = Depends(get_db)):
    detail = 'third_view'
    user = db.query(User).filter_by(email=email).first()
    if not user:
        flash(request, "Something went wrong.", {"heading": "Error!", "tag": "error"})
        return RedirectResponse(request.url_for("login"))
    
    await Util.send_password_reset_email(backgroundtasks, request, user, db)
    return templates.TemplateResponse('accounts/password-reset-request.html', detail=detail, form=None)
