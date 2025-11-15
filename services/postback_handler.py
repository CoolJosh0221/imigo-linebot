"""Postback handler for Rich Menu actions (MVP)"""

import logging
from typing import Optional
from linebot.v3.messaging import (
    AsyncApiClient,
    ReplyMessageRequest,
    TextMessage,
    QuickReply,
    QuickReplyItem,
    MessageAction,
)
from database.database import DatabaseService
from services.maps_service import MapsService
from config import BotConfig

log = logging.getLogger(__name__)


class PostbackHandler:
    """Handles Rich Menu postback events"""

    # Location category mappings
    LOCATION_CATEGORIES = {
        "location_food": {
            "id": "restoran Indonesia",
            "zh": "印尼餐廳",
            "en": "Indonesian restaurant",
            "search_type": "indonesian_restaurant",
        },
        "location_health": {
            "id": "rumah sakit",
            "zh": "醫院",
            "en": "hospital",
            "search_type": "hospital",
        },
        "location_community": {
            "id": "masjid",
            "zh": "清真寺",
            "en": "mosque",
            "search_type": "mosque",
        },
        "location_emergency": {
            "id": "layanan darurat",
            "zh": "緊急服務",
            "en": "emergency services",
            "search_type": "police",
        },
        "location_services": {
            "id": "ATM/Bank",
            "zh": "ATM/銀行",
            "en": "ATM/Bank",
            "search_type": "atm",
        },
    }

    def __init__(
        self,
        db_service: DatabaseService,
        maps_service: MapsService,
        config: BotConfig,
        line_api: AsyncApiClient,
    ):
        self.db_service = db_service
        self.maps_service = maps_service
        self.config = config
        self.line_api = line_api

    async def handle_postback(
        self,
        reply_token: str,
        user_id: str,
        postback_data: str,
        user_location: Optional[dict] = None,
    ) -> bool:
        """
        Handle postback event from Rich Menu.

        Args:
            reply_token: Reply token
            user_id: User ID
            postback_data: Postback data string
            user_location: Optional user location dict with latitude/longitude

        Returns:
            True if handled, False otherwise
        """
        # Get user language
        user_lang = await self.db_service.get_user_language(user_id)

        # Handle different postback types
        if postback_data.startswith("location_"):
            return await self._handle_location_query(
                reply_token, user_id, user_lang, postback_data, user_location
            )
        elif postback_data == "change_language":
            return await self._handle_language_change(
                reply_token, user_id, user_lang
            )
        elif postback_data == "clear_chat":
            return await self._handle_clear_chat(reply_token, user_id, user_lang)

        return False

    async def _handle_location_query(
        self,
        reply_token: str,
        user_id: str,
        user_lang: str,
        category: str,
        user_location: Optional[dict] = None,
    ) -> bool:
        """
        Handle location query postback.

        Args:
            reply_token: Reply token
            user_id: User ID
            user_lang: User language
            category: Location category (e.g., "location_food")
            user_location: Optional user location

        Returns:
            True if handled
        """
        if category not in self.LOCATION_CATEGORIES:
            return False

        category_info = self.LOCATION_CATEGORIES[category]
        category_name = category_info[user_lang]
        search_type = category_info["search_type"]

        # Check if we have user location
        if not user_location:
            # Ask user to share location
            message = self._get_location_request_message(user_lang, category_name)
            await self._send_reply(reply_token, message)
            return True

        # Search for nearby places
        searching_msg = self.config.get_message("location_searching").format(
            category=category_name
        )
        await self._send_reply(reply_token, searching_msg)

        latitude = user_location.get("latitude")
        longitude = user_location.get("longitude")

        places = await self.maps_service.find_nearby_places(
            category=search_type,
            latitude=latitude,
            longitude=longitude,
            radius=5000,  # 5km
            language=user_lang,
        )

        # Format and send results
        result_message = self.maps_service.format_places_message(
            places, category_name, user_lang
        )
        await self._send_reply(reply_token, result_message)

        log.info(
            f"Sent {len(places)} {category_name} results to user {user_id[:8]}"
        )
        return True

    async def _handle_language_change(
        self, reply_token: str, user_id: str, current_lang: str
    ) -> bool:
        """
        Handle language change postback.

        Args:
            reply_token: Reply token
            user_id: User ID
            current_lang: Current language

        Returns:
            True if handled
        """
        # Send language selection quick reply
        quick_reply_items = [
            QuickReplyItem(
                action=MessageAction(label="🇮🇩 Indonesian", text="/lang id")
            ),
            QuickReplyItem(
                action=MessageAction(label="🇹🇼 中文", text="/lang zh")
            ),
            QuickReplyItem(
                action=MessageAction(label="🇺🇸 English", text="/lang en")
            ),
        ]

        quick_reply = QuickReply(items=quick_reply_items)

        message_text = {
            "id": "Pilih bahasa Anda:",
            "zh": "選擇您的語言：",
            "en": "Choose your language:",
        }.get(current_lang, "Pilih bahasa Anda:")

        await self.line_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[
                    TextMessage(text=message_text, quick_reply=quick_reply)
                ],
            )
        )

        log.info(f"Sent language selection to user {user_id[:8]}")
        return True

    async def _handle_clear_chat(
        self, reply_token: str, user_id: str, user_lang: str
    ) -> bool:
        """
        Handle clear chat postback.

        Args:
            reply_token: Reply token
            user_id: User ID
            user_lang: User language

        Returns:
            True if handled
        """
        # Clear conversation history
        await self.db_service.clear_user_conversation(user_id)

        # Send confirmation
        message = self.config.get_message("cleared")
        await self._send_reply(reply_token, message)

        log.info(f"Cleared conversation for user {user_id[:8]}")
        return True

    def _get_location_request_message(
        self, language: str, category: str
    ) -> str:
        """
        Get message requesting user to share location.

        Args:
            language: User language
            category: Category name

        Returns:
            Message text
        """
        messages = {
            "id": f"📍 Untuk mencari {category} terdekat, silakan bagikan lokasi Anda menggunakan LINE.\n\nKetuk ikon '+' di sebelah kotak pesan, lalu pilih 'Location'.",
            "zh": f"📍 要尋找附近的{category}，請使用 LINE 分享您的位置。\n\n點擊訊息框旁的 '+' 圖示，然後選擇「位置」。",
            "en": f"📍 To find nearby {category}, please share your location using LINE.\n\nTap the '+' icon next to the message box, then select 'Location'.",
        }
        return messages.get(language, messages["id"])

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
