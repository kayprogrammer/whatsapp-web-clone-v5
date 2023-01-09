from sqlalchemy import Column, Integer, DateTime, String, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Session, relationship

from apps.accounts.models import User

from apps.common.models import TimeStampedUUIDModel


class Message(TimeStampedUUIDModel):
    __tablename__ = 'message'

    sender_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'))
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sender_messages")

    receiver_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'))
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="receiver_messages")

    text = Column(Text(), nullable=True)

    vn = Column(String(), nullable=True)
    file = Column(String(), nullable=True)

    is_read = Column(Boolean, default=False)

    def __repr__(self):
        return f"Message by {self.sender.name} to {self.receiver.name} : {self.text}"