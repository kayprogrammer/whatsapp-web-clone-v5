from sqladmin import ModelView
from setup.main import admin
from . models import User, Timezone, Otp, BlockedContact

class TimezoneAdmin(ModelView, model=Timezone):
    column_list = [Timezone.pkid, Timezone.id, Timezone.name]

class UserAdmin(ModelView, model=User):
    column_list = [User.pkid, User.id, User.name, User.email, User.phone]

class OtpAdmin(ModelView, model=Otp):
    column_list = [Otp.pkid, Otp.user_id, Otp.value]

class BlockedContactAdmin(ModelView, model=BlockedContact):
    column_list = [BlockedContact.pkid, BlockedContact.blocker_id, BlockedContact.blockee_id]

admin.add_view(TimezoneAdmin)
admin.add_view(UserAdmin)
admin.add_view(OtpAdmin)
admin.add_view(BlockedContactAdmin)