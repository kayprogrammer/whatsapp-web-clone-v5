from sqlalchemy import Column, Integer, DateTime, String, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property

from apps.accounts.models import User

from apps.common.models import TimeStampedUUIDModel


class Message(TimeStampedUUIDModel):
    __tablename__ = 'message'

    sender_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'))
    receiver_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'))

    text = Column(Text(), nullable=True)

    vn = Column(String(), nullable=True)
    file = Column(String(), nullable=True)

    is_read = Column(Boolean, default=False)

    # def __init__(self, sender_id, receiver_id, text, **kwargs):
    #     super().__init__(sender_id=sender_id, receiver_id=receiver_id, text=text, **kwargs)

    @property
    def sender(self):
        return User.query.filter_by(id=self.sender_id).first()

    @property
    def receiver(self):
        return User.query.filter_by(id=self.receiver_id).first()

    def __repr__(self):
        return f"Message by {self.sender.name} to {self.receiver.name} : {self.text}"