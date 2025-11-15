from sqlalchemy import Column, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())


class UserPreferences(Base):
    __tablename__ = "user_preferences"

    user_id = Column(String, primary_key=True)
    language = Column(String, nullable=False, default="en")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class GroupSettings(Base):
    """Group translation settings for LINE group chats"""
    __tablename__ = "group_settings"

    group_id = Column(String, primary_key=True)
    translate_enabled = Column(Boolean, default=False)
    target_language = Column(String, default="zh")  # id, zh, en
    enabled_by = Column(String)  # user_id who enabled translation
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
