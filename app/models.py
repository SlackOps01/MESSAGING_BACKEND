from .database import Base
from sqlalchemy import Column, String, Enum as SQLEnum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4
from .schemas import Role

class Users(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(100), nullable=False)
    role = Column(SQLEnum(Role), default=Role.user)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    date_updated = Column(DateTime(timezone=True), server_onupdate=func.now())

    messages_sent = relationship(
        "Messages",
        back_populates="sender",
        foreign_keys=lambda: [Messages.sender_id],
        cascade="all, delete-orphan"
    )

    messages_received = relationship(
        "Messages",
        back_populates="recipient",
        foreign_keys=lambda: [Messages.recipient_id],
        cascade="all, delete-orphan"
    )

class Messages(Base):
    __tablename__ = "messages"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    sender_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    recipient_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    content = Column(String(200), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    sender = relationship(
        "Users",
        back_populates="messages_sent",
        foreign_keys=[sender_id]
    )
    recipient = relationship(
        "Users",
        back_populates="messages_received",
        foreign_keys=[recipient_id]
    )


