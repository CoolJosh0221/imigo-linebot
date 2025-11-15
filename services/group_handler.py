"""Group chat handler for employer-controlled translation (MVP)"""

import logging
import re
from typing import Optional
from linebot.v3.messaging import AsyncApiClient, ReplyMessageRequest, TextMessage
from database.database import DatabaseService
from services.translation_service import TranslationService
from config import BotConfig

log = logging.getLogger(__name__)


class GroupHandler:
    """Handles group chat messages and employer-controlled translation"""

    def __init__(
        self,
        db_service: DatabaseService,
        translation_service: TranslationService,
        config: BotConfig,
        line_api: AsyncApiClient,
    ):
        self.db_service = db_service
        self.translation_service = translation_service
        self.config = config
        self.line_api = line_api

    async def handle_group_message(
        self,
        event,
        reply_token: str,
        group_id: str,
        user_id: str,
        text: str,
    ) -> bool:
        """
        Handle group chat message.

        Args:
            event: LINE event object
            reply_token: Reply token for sending response
            group_id: Group ID
            user_id: User ID who sent the message
            text: Message text

        Returns:
            True if message was handled, False otherwise
        """
        # Check for /translate commands (employer/admin only)
        if text.startswith("/translate"):
            return await self._handle_translate_command(
                event, reply_token, group_id, user_id, text
            )

        # Check if auto-translation is enabled for this group
        settings = await self.db_service.get_group_settings(group_id)
        if settings and settings.get("translation_enabled"):
            target_lang = settings.get("target_language")
            if target_lang:
                await self._auto_translate_message(
                    reply_token, text, target_lang
                )
                return True

        return False

    async def _handle_translate_command(
        self,
        event,
        reply_token: str,
        group_id: str,
        user_id: str,
        text: str,
    ) -> bool:
        """
        Handle /translate command (admin only).

        Commands:
        - /translate on <language> - Enable auto-translation
        - /translate off - Disable auto-translation

        Args:
            event: LINE event object
            reply_token: Reply token
            group_id: Group ID
            user_id: User ID
            text: Command text

        Returns:
            True if command was handled
        """
        # Check if user is admin/owner
        is_admin = await self._check_if_admin(event, group_id, user_id)
        if not is_admin:
            await self._send_reply(
                reply_token, self.config.get_message("admin_only")
            )
            return True

        # Parse command
        match = re.match(r"/translate\s+(on|off)(?:\s+(\w+))?", text.lower())
        if not match:
            await self._send_reply(
                reply_token,
                "Usage:\n/translate on <language>\n/translate off\n\nLanguages: id, zh, en",
            )
            return True

        action = match.group(1)
        language = match.group(2)

        if action == "on":
            if not language:
                await self._send_reply(
                    reply_token,
                    "Please specify target language:\n/translate on id\n/translate on zh\n/translate on en",
                )
                return True

            # Validate language
            if language not in ["id", "zh", "en"]:
                await self._send_reply(
                    reply_token,
                    f"Invalid language: {language}\nSupported: id (Indonesian), zh (Chinese), en (English)",
                )
                return True

            # Enable translation
            await self.db_service.set_group_translation(
                group_id, enabled=True, target_language=language
            )

            lang_name = self.translation_service.get_language_name(language)
            message = self.config.get_message("translation_enabled").format(
                language=lang_name
            )
            await self._send_reply(reply_token, message)
            log.info(f"Group {group_id[:8]} enabled translation to {language}")
            return True

        elif action == "off":
            # Disable translation
            await self.db_service.set_group_translation(
                group_id, enabled=False, target_language=None
            )

            message = self.config.get_message("translation_disabled")
            await self._send_reply(reply_token, message)
            log.info(f"Group {group_id[:8]} disabled translation")
            return True

        return False

    async def _auto_translate_message(
        self, reply_token: str, text: str, target_lang: str
    ) -> None:
        """
        Auto-translate message and send as reply.

        Args:
            reply_token: Reply token
            text: Message text to translate
            target_lang: Target language code
        """
        try:
            # Auto-detect source language and translate
            translated = await self.translation_service.auto_detect_and_translate(
                text, target_lang
            )

            # Only send if translation is different from original
            if translated and translated != text:
                await self._send_reply(reply_token, f"📝 {translated}")
                log.debug(f"Auto-translated to {target_lang}")

        except Exception as e:
            log.error(f"Auto-translation error: {e}")

    async def _check_if_admin(
        self, event, group_id: str, user_id: str
    ) -> bool:
        """
        Check if user is group admin or owner.

        Args:
            event: LINE event object
            group_id: Group ID
            user_id: User ID

        Returns:
            True if user is admin, False otherwise
        """
        try:
            # Get group summary to check member roles
            # Note: This requires the LINE Messaging API
            # For MVP, we'll use a simple check based on event source type
            # In production, you should use:
            # group_summary = await self.line_api.get_group_summary(group_id)
            # member = await self.line_api.get_group_member_profile(group_id, user_id)

            # MVP: Simple check - if event has source type "group", allow first message sender
            # In production, implement proper admin checking via LINE API
            # For now, return True to allow testing
            # TODO: Implement proper admin checking in production

            return True  # MVP: Allow all users for testing

        except Exception as e:
            log.error(f"Error checking admin status: {e}")
            return False

    async def _send_reply(self, reply_token: str, message: str) -> None:
        """
        Send reply message.

        Args:
            reply_token: Reply token
            message: Message text
        """
        try:
            await self.line_api.reply_message(
                ReplyMessageRequest(
                    reply_token=reply_token, messages=[TextMessage(text=message)]
                )
            )
        except Exception as e:
            log.error(f"Error sending reply: {e}")
