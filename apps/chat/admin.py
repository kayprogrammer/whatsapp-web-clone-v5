from sqladmin import ModelView
from setup.main import admin
from . models import Message

class MessageAdmin(ModelView, model=Message):
    column_list = [Message.sender, Message.receiver, Message.text, Message.vn, Message.file, Message.is_read]

admin.add_view(MessageAdmin)