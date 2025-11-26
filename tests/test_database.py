"""Tests for database service"""
import pytest
from database.database import DatabaseService
from datetime import datetime, timedelta


@pytest.fixture
async def db_service():
    """Create a test database service"""
    service = DatabaseService(db_url="sqlite+aiosqlite:///:memory:")
    await service.init_db()
    yield service
    await service.dispose()


class TestDatabaseService:
    """Test DatabaseService class"""

    @pytest.mark.asyncio
    async def test_save_and_get_conversation(self, db_service):
        """Test saving and retrieving conversation history"""
        user_id = "test_user_123"

        # Save messages
        await db_service.save_message(user_id, "user", "Hello")
        await db_service.save_message(user_id, "assistant", "Hi there!")

        # Retrieve history
        history = await db_service.get_conversation_history(user_id)

        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Hello"
        assert history[1]["role"] == "assistant"
        assert history[1]["content"] == "Hi there!"

    @pytest.mark.asyncio
    async def test_conversation_history_limit(self, db_service):
        """Test conversation history limit"""
        user_id = "test_user_456"

        # Save 15 messages
        for i in range(15):
            await db_service.save_message(user_id, "user", f"Message {i}")

        # Retrieve with limit of 10
        history = await db_service.get_conversation_history(user_id, limit=10)

        assert len(history) == 10
        # Should get the most recent 10 messages
        assert history[0]["content"] == "Message 5"
        assert history[-1]["content"] == "Message 14"

    @pytest.mark.asyncio
    async def test_clear_user_conversation(self, db_service):
        """Test clearing user conversation"""
        user_id = "test_user_789"

        # Save messages
        await db_service.save_message(user_id, "user", "Hello")
        await db_service.save_message(user_id, "assistant", "Hi!")

        # Clear conversation
        count = await db_service.clear_user_conversation(user_id)
        assert count == 2

        # Verify cleared
        history = await db_service.get_conversation_history(user_id)
        assert len(history) == 0

    @pytest.mark.asyncio
    async def test_set_and_get_user_language(self, db_service):
        """Test setting and getting user language preference"""
        user_id = "test_user_lang"

        # Initially no language set
        lang = await db_service.get_user_language(user_id)
        assert lang is None

        # Set language
        await db_service.set_user_language(user_id, "en")

        # Retrieve language
        lang = await db_service.get_user_language(user_id)
        assert lang == "en"

        # Update language
        await db_service.set_user_language(user_id, "zh")
        lang = await db_service.get_user_language(user_id)
        assert lang == "zh"

    @pytest.mark.asyncio
    async def test_group_translation_settings(self, db_service):
        """Test group translation settings"""
        group_id = "test_group_123"
        user_id = "test_user_admin"

        # Initially no settings
        settings = await db_service.get_group_settings(group_id)
        assert settings is None

        # Enable translation
        await db_service.enable_group_translation(group_id, "zh", user_id)

        # Get settings
        settings = await db_service.get_group_settings(group_id)
        assert settings is not None
        assert settings["translate_enabled"] is True
        assert settings["target_language"] == "zh"
        assert settings["enabled_by"] == user_id

        # Disable translation
        await db_service.disable_group_translation(group_id)

        # Verify disabled
        settings = await db_service.get_group_settings(group_id)
        assert settings["translate_enabled"] is False

    @pytest.mark.asyncio
    async def test_cleanup_old_conversations(self, db_service):
        """Test cleaning up old conversations"""
        user_id = "test_user_cleanup"

        # Save a message
        await db_service.save_message(user_id, "user", "Old message")

        # Try to clean up messages older than 30 days
        # (this won't delete our message since it's recent)
        count = await db_service.cleanup_old_conversations(days_old=30)

        # Our recent message should still be there
        history = await db_service.get_conversation_history(user_id)
        assert len(history) == 1

    @pytest.mark.asyncio
    async def test_multiple_users_isolation(self, db_service):
        """Test that different users' data is isolated"""
        user1 = "user_001"
        user2 = "user_002"

        # Save messages for different users
        await db_service.save_message(user1, "user", "User 1 message")
        await db_service.save_message(user2, "user", "User 2 message")

        # Set different languages
        await db_service.set_user_language(user1, "en")
        await db_service.set_user_language(user2, "zh")

        # Verify isolation
        history1 = await db_service.get_conversation_history(user1)
        history2 = await db_service.get_conversation_history(user2)

        assert len(history1) == 1
        assert len(history2) == 1
        assert history1[0]["content"] == "User 1 message"
        assert history2[0]["content"] == "User 2 message"

        lang1 = await db_service.get_user_language(user1)
        lang2 = await db_service.get_user_language(user2)

        assert lang1 == "en"
        assert lang2 == "zh"
