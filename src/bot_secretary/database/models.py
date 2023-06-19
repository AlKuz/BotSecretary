from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()


class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    users = relationship('User', backref='role', cascade='all, delete-orphan')

    @hybrid_property
    def is_exist(self) -> bool:
        return self.id is not None


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(120), nullable=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'))

    messages = relationship('Message', backref='user', cascade='all, delete-orphan')


class MessageType(Base):
    __tablename__ = 'message_types'

    id = Column(Integer, primary_key=True)
    type = Column(String(50), unique=True, nullable=False)

    messages = relationship('Message', backref='message_type', cascade='all, delete-orphan')

    @hybrid_property
    def is_exist(self) -> bool:
        return self.id is not None


class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    content = Column(String(500), nullable=False)
    timestamp = Column(DateTime, server_default=func.now())
    user_id = Column(Integer, ForeignKey('users.id'))
    message_type_id = Column(Integer, ForeignKey('message_types.id'))
    responding_to = Column(Integer, ForeignKey('messages.id'))

    responding_message = relationship('Message', remote_side=[id], cascade='all, delete-orphan')
