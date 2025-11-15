from __future__ import annotations
import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from database.models import Base, Conversation, UserPreferences, GroupSettings

log = logging.getLogger(__name__)


class DatabaseService:
    """Async SQLAlchemy ORM wrapper."""

    def __init__(
        self, db_url: str = "sqlite+aiosqlite:///database.db", echo: bool = False
    ):
        self.engine = create_async_engine(url=db_url, echo=echo)
        self.Session: async_sessionmaker[AsyncSession] = async_sessionmaker(
            self.engine, expire_on_commit=False
        )

    async def init_db(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        log.info("DB init ok")

    async def dispose(self) -> None:
        await self.engine.dispose()

    async def save_message(self, user_id: str, role: str, content: str) -> None:
        async with self.Session() as s, s.begin():
            s.add(Conversation(user_id=user_id, role=role, content=content))
        log.debug("Saved %s for user %s", role, user_id[:8])

    async def get_conversation_history(
        self, user_id: str, limit: int = 10
    ) -> list[dict]:
        async with self.Session() as s:
            rows = list(
                await s.scalars(
                    select(Conversation)
                    .where(Conversation.user_id == user_id)
                    .order_by(Conversation.created_at.desc())
                    .limit(limit)
                )
            )
        rows.reverse()
        return [
            {"role": r.role, "content": r.content, "timestamp": r.created_at}
            for r in rows
        ]

    async def clear_user_conversation(self, user_id: str) -> int:
        async with self.Session() as s, s.begin():
            res = await s.execute(
                delete(Conversation).where(Conversation.user_id == user_id)
            )
            count = res.rowcount or 0
        log.info("Cleared %d messages for user %s", count, user_id[:8])
        return count

    async def cleanup_old_conversations(self, days_old: int = 30) -> int:
        cutoff = datetime.now() - timedelta(days=days_old)
        async with self.Session() as s, s.begin():
            res = await s.execute(
                delete(Conversation).where(Conversation.created_at < cutoff)
            )
            count = res.rowcount or 0
        log.info("Cleaned %d old messages", count)
        return count

    async def set_user_language(self, user_id: str, language: str) -> None:
        async with self.Session() as s, s.begin():
            pref = await s.scalar(
                select(UserPreferences).where(UserPreferences.user_id == user_id)
            )
            if pref:
                pref.language = language
                pref.updated_at = datetime.now()
            else:
                s.add(UserPreferences(user_id=user_id, language=language))
        log.info("Set language=%s for user %s", language, user_id[:8])

    async def get_user_language(self, user_id: str) -> str:
        async with self.Session() as s:
            lang: Optional[str] = await s.scalar(
                select(UserPreferences.language).where(
                    UserPreferences.user_id == user_id
                )
            )
        return lang or "en"

    # Group translation methods
    async def enable_group_translation(
        self, group_id: str, target_language: str, enabled_by: str
    ) -> None:
        """Enable translation for a group chat"""
        async with self.Session() as s, s.begin():
            settings = await s.scalar(
                select(GroupSettings).where(GroupSettings.group_id == group_id)
            )
            if settings:
                settings.translate_enabled = True
                settings.target_language = target_language
                settings.enabled_by = enabled_by
                settings.updated_at = datetime.now()
            else:
                s.add(
                    GroupSettings(
                        group_id=group_id,
                        translate_enabled=True,
                        target_language=target_language,
                        enabled_by=enabled_by,
                    )
                )
        log.info(
            "Enabled translation for group %s to %s", group_id[:8], target_language
        )

    async def disable_group_translation(self, group_id: str) -> None:
        """Disable translation for a group chat"""
        async with self.Session() as s, s.begin():
            settings = await s.scalar(
                select(GroupSettings).where(GroupSettings.group_id == group_id)
            )
            if settings:
                settings.translate_enabled = False
                settings.updated_at = datetime.now()
        log.info("Disabled translation for group %s", group_id[:8])

    async def get_group_settings(self, group_id: str) -> Optional[dict]:
        """Get translation settings for a group"""
        async with self.Session() as s:
            settings = await s.scalar(
                select(GroupSettings).where(GroupSettings.group_id == group_id)
            )
            if settings:
                return {
                    "translate_enabled": settings.translate_enabled,
                    "target_language": settings.target_language,
                    "enabled_by": settings.enabled_by,
                }
        return None
