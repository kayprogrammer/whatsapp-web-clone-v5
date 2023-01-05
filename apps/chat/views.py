from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles

from sqlalchemy.orm import Session
from sqlalchemy import or_, case, literal_column
from apps.accounts.models import User
from apps.accounts.views import get_current_user
from fastapi import Depends
from fastapi.templating import Jinja2Templates
from fastapi_csrf_protect import CsrfProtect

from pathlib import Path

from setup.extensions import get_flashed_messages, flash
from setup.database import get_db

from . models import Message
from . emojis import emojis
import json
import pytz

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "templates"
chatrouter = APIRouter(tags=['chat'])
templates = Jinja2Templates(directory=TEMPLATE_DIR)
templates.env.globals['get_flashed_messages'] = get_flashed_messages

# @chatrouter.before_request
# @login_required
# def before_request():
#     """ Execute before all of the chat endpoints. """
#     session['current_path'] = request.path
#     pass 

@chatrouter.api_route('/home', methods=['GET', 'POST'])
async def home(request: Request, user: User = Depends(get_current_user), csrf_protect:CsrfProtect = Depends()):    
    messages = Message.query.filter(
        or_(Message.sender_id == user.id, Message.receiver_id == user.id)
    )
    other = case(
        [(Message.sender_id == user.id, literal_column("receiver_id") )], 
        else_=literal_column("sender_id")
    )
    inbox_list = messages.order_by(
        other, Message.created_at.desc()
    ).distinct(other)
    sorted_inbox_list = sorted(inbox_list, key=lambda x: x.created_at, reverse=True)
    
    all_users = User.query.filter(User.is_email_verified==True, User.is_phone_verified==True, User.is_active==True, User.id != user.id).order_by('name')

    return templates.TemplateResponse('chat/index.html', {'request': request, 'user':user, 'all_users':all_users, 'inbox_list': sorted_inbox_list, 'messages': messages, 'csrf_token': csrf_protect.generate_csrf()})

@chatrouter.api_route('/show-direct-messages', methods=['POST'])
async def show_dms(request: Request, response_class = HTMLResponse, user: User = Depends(get_current_user), db: Session = Depends(get_db), csrf_protect:CsrfProtect = Depends()):
    form_data = await request.form()
    phone = form_data.get('phone')
    friend = User.query.filter_by(phone=phone).first()
    if not friend:
        return {'error':  'User not found'} 

    recent_emojis = request.session.get('recent_emojis')
    messages = Message.query.filter(
        or_(Message.sender_id == user.id, Message.receiver_id == user.id), 
        or_(Message.sender_id == friend.id, Message.receiver_id == friend.id)
    )
    messages.filter_by(sender_id=friend.id).update(dict(is_read=True))
    db.commit()
    messages = messages.order_by(Message.created_at)
    response = dict()
    
    response['success'] = True
    response['html_data'] = templates.TemplateResponse('chat/dm-page.html', {'request': request, 'messages':messages, 'friend':friend, 'recent_emojis': recent_emojis, 'user': user, 'csrf_token': csrf_protect.generate_csrf()})
    print(response)    
    return response

@chatrouter.route('/send-message', methods=['POST'])
async def send_message(request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db), csrf_protect:CsrfProtect = Depends()):
    data = await request.form()
    message = data.get('message')
    friend = User.query.filter_by(phone=data.get('phone')).first()
    if not friend:
        return {'error': 'User not found'} 
    if len(message) < 1:
        return {'error': "You didn't type anything"}

    # Solve recent emojis
    recent_emojis = request.session.get('recent_emojis')
    em = []
    for i in message:
        if i in emojis:
            if recent_emojis and i in recent_emojis:
                recent_emojis.remove(i)
            em.append(i)
            

    if len(em) > 0:
        em = list(set(em)) # remove duplicates
        if recent_emojis:
            updated_emojis = em + recent_emojis
            if len(updated_emojis) > 50:
                n = len(updated_emojis) - 50
                del updated_emojis[-n:]
            request.session['recent_emojis'] = updated_emojis
        else:
            updated_emojis = em
            if len(updated_emojis) > 50:
                n = len(updated_emojis) - 50
                del updated_emojis[-n:]
            request.session['recent_emojis'] = updated_emojis

    message_object = Message(sender_id=user.id, receiver_id=friend.id, text=message)
    db.add(message_object)
    db.commit()
    time = message_object.created_at.astimezone(pytz.timezone(user.tzname))
    return {'success': True, 'message': message, 'time': time.strftime('%I:%M %p')}
