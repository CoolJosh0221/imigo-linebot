from sqlalchemy import Column, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


class Conversation(Base):
    """Stores conversation history for personal chats only (not group chats)"""
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())


class UserPreferences(Base):
    """Stores user language preferences for personal chats"""
    __tablename__ = "user_preferences"

    user_id = Column(String, primary_key=True)
    language = Column(String, nullable=False, default="id")  # Default: Indonesian
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class GroupSettings(Base):
    """Stores group chat translation settings (employer-controlled)"""
    __tablename__ = "group_settings"

    group_id = Column(String, primary_key=True)
    translation_enabled = Column(Boolean, nullable=False, default=False)
    target_language = Column(String, nullable=True)  # "id", "zh", or "en"
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
