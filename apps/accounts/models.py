from sqlalchemy import Column, Integer, DateTime, String, Boolean, ForeignKey, UniqueConstraint

from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.hybrid import hybrid_property
import sqlalchemy.types as types

from apps.common.models import TimeStampedUUIDModel

from datetime import datetime

from . hashers import Hasher

from . validators import *
from . choices import *

class Timezone(TimeStampedUUIDModel):
    __tablename__ = 'timezone'
    name = Column(String(), nullable=True)
    timezones = relationship('User', foreign_keys="User.tz_id", back_populates='tz', lazy=True)
    
    def __repr__(self):
        return '<Timezone %r>' % self.name

from . managers import UserManager, OtpManager # Leave this here cos of some circular imports error

class ChoiceType(types.TypeDecorator):

    impl = types.String

    def __init__(self, choices, **kw):
        self.choices = dict(choices)
        super(ChoiceType, self).__init__(**kw)

    def process_bind_param(self, value, dialect):
        l = [k for k, v in self.choices.items() if v == value]

        if len(l) < 1:
            raise ValueError('Invalid Choice')
        return l[0]

    def process_result_value(self, value, dialect):
        return self.choices[value]

class User(UserManager, TimeStampedUUIDModel):
    __tablename__ = 'users'

    name = Column(String(50))
    email = Column(String(), unique=True)
    phone = Column(String(20), unique=True)
    password = Column(String())
    tz_id = Column(Integer(), ForeignKey('timezone.pkid', ondelete='SET NULL'))
    tz = relationship("Timezone", foreign_keys=[tz_id], back_populates="timezones")
    avatar = Column(String(), default="https://res.cloudinary.com/kay-development/image/upload/v1667610903/whatsappclonev1/default/Avatar-10_mvq1cm.jpg")
    theme = Column(ChoiceType(THEME_CHOICES), default="DARK")
    wallpaper = Column(String(), default="https://res.cloudinary.com/kay-development/image/upload/v1670371074/whatsappwebclonev4/bg-chat_lrn705.png")
    status = Column(String(300), default="Hey There! I'm using Whatsapp Web Clone V5!")

    #---Privacy Settings---#
    last_seen = Column(ChoiceType(PRIVACYCHOICES.last_seen), default="EVERYONE")
    avatar_status = Column(ChoiceType(PRIVACYCHOICES.avatar_status), default="EVERYONE")
    about_status = Column(ChoiceType(PRIVACYCHOICES.about_status), default="EVERYONE")
    group_status = Column(ChoiceType(PRIVACYCHOICES.groups_status), default="EVERYONE")
    message_timer = Column(ChoiceType(PRIVACYCHOICES.message_timer), default="OFF")
    read_receipts = Column(Boolean, default=True)
    blocked_contacts_count = Column(Integer, default="0")
    #----------------------#

    #---Notification Settings---#
    message_notifications = Column(Boolean, default=True)
    show_previews = Column(Boolean, default=True)
    show_reaction_notifications = Column(Boolean, default=True)
    sounds = Column(Boolean, default=True)
    security_notifications = Column(Boolean, default=True)
    #----------------------#

    current_activation_jwt = Column(MutableDict.as_mutable(JSONB), default={'token': "", 'used': False})
    current_password_jwt = Column(MutableDict.as_mutable(JSONB), default={'token': "", 'used': False})

    otp = relationship("Otp", uselist=False, backref="user", cascade="all,delete")
    terms_agreement = Column(Boolean, default=False)
    is_email_verified = Column(Boolean, default=False)
    is_phone_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_online = Column(DateTime, default=datetime.now)

    blocker_blockedcontacts = relationship('BlockedContact', foreign_keys="BlockedContact.blocker_id", back_populates='blocker', lazy=True)
    blockee_blockedcontacts = relationship('BlockedContact', foreign_keys="BlockedContact.blockee_id", back_populates='blockee', lazy=True)

    sender_messages = relationship('Message', foreign_keys="Message.sender_id", back_populates='sender', lazy=True, passive_deletes=True)
    receiver_messages = relationship('Message', foreign_keys="Message.receiver_id", back_populates='receiver', lazy=True, passive_deletes=True)


    def __repr__(self):
        return self.name

    @property
    def tzname(self):
        tz_name = self.tz.name
        if tz_name:
            return tz_name
        return 'UTC'

    def check_password(self, value):
        """Check password."""
        return Hasher.verify_password(value, self.password)
class Otp(OtpManager, TimeStampedUUIDModel):
    __tablename__ = 'otp'

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'))
    value = Column(Integer())

class BlockedContact(TimeStampedUUIDModel):
    __tablename__ = 'blockedcontact'

    blocker_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    blocker = relationship("User", foreign_keys=[blocker_id], back_populates="blocker_blockedcontacts")

    blockee_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    blockee = relationship("User", foreign_keys=[blockee_id], back_populates="blockee_blockedcontacts")

    def __repr__(self):
        try:
            return f"{self.blocker_id} blocked {self.blockee_id}"
        except:
            return "Block issues"    

    __table_args__ = (UniqueConstraint('blocker_id', 'blockee_id'), )
