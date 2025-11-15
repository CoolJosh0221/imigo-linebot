"""Imigo LINE Bot - MVP (Translation + Location Services)"""

import logging
import re
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request, HTTPException

from linebot.v3.webhook import WebhookParser
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    AsyncApiClient,
    AsyncMessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import (
    MessageEvent,
    PostbackEvent,
    TextMessageContent,
    LocationMessageContent,
)

from database.database import DatabaseService
from services.ai_service import AIService
from services.translation_service import TranslationService
from services.maps_service import MapsService
from services.group_handler import GroupHandler
from services.postback_handler import PostbackHandler
from config import load_config, get_config

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Global services
db_service: DatabaseService
ai_service: AIService
translation_service: TranslationService
maps_service: MapsService
group_handler: GroupHandler
postback_handler: PostbackHandler

app = FastAPI(title="Imigo LINE Bot", version="1.0.0-mvp")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup services"""
    global db_service, ai_service, translation_service, maps_service
    global group_handler, postback_handler

    cfg = load_config()

    # Initialize database
    db_service = DatabaseService()
    await db_service.init_db()

    # Initialize AI and translation services
    ai_service = AIService(db_service, cfg)
    translation_service = TranslationService()
    maps_service = MapsService()

    # Get LINE API client
    line_api, _ = get_line_api()

    # Initialize handlers
    group_handler = GroupHandler(db_service, translation_service, cfg, line_api)
    postback_handler = PostbackHandler(db_service, maps_service, cfg, line_api)

    log.info(f"🚀 {cfg.bot.name} started (MVP)")
    log.info(f"   Language: {cfg.bot.language}")
    log.info(f"   Features: Translation + Location")
    yield

    await db_service.dispose()
    log.info("Services closed")


app.router.lifespan_context = lifespan


def get_line_api():
    cfg = get_config()
    line_config = Configuration(access_token=cfg.line_token)
    async_client = AsyncApiClient(line_config)
    return AsyncMessagingApi(async_client), WebhookParser(cfg.line_secret)


@app.get("/")
async def root():
    cfg = get_config()
    return {
        "status": "running",
        "bot": cfg.bot.name,
        "language": cfg.bot.language,
        "country": cfg.bot.country,
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


async def handle_text_message(event: MessageEvent) -> None:
    """Handle text messages (personal or group chat)"""
    cfg = get_config()
    line_api, _ = get_line_api()

    user_id = event.source.user_id
    text = event.message.text
    reply_token = event.reply_token

    # Determine if this is a group chat
    source_type = event.source.type
    is_group = source_type in ["group", "room"]
    group_id = getattr(event.source, "group_id", None) if is_group else None

    # Handle group chat
    if is_group and group_id:
        handled = await group_handler.handle_group_message(
            event, reply_token, group_id, user_id, text
        )
        if handled:
            return

    # Personal chat - check for commands
    if text.startswith("/"):
        await handle_command(event, user_id, text, reply_token, line_api)
        return

    # Personal chat - check if user is new
    lang = await db_service.get_user_language(user_id)
    if not lang:
        await db_service.set_user_language(user_id, cfg.bot.language)
        await line_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text=cfg.get_message("welcome"))],
            )
        )
        return

    # Generate AI response
    reply = await ai_service.generate_response(user_id, text)

    await line_api.reply_message(
        ReplyMessageRequest(
            reply_token=reply_token, messages=[TextMessage(text=reply)]
        )
    )


async def handle_location_message(event: MessageEvent) -> None:
    """Handle location messages (for finding nearby places)"""
    cfg = get_config()
    line_api, _ = get_line_api()

    user_id = event.source.user_id
    reply_token = event.reply_token

    # Get user language
    user_lang = await db_service.get_user_language(user_id)

    # Get location
    location = {
        "latitude": event.message.latitude,
        "longitude": event.message.longitude,
    }

    # Store location temporarily (could be used for future queries)
    # For now, just acknowledge it
    message = {
        "id": "📍 Lokasi diterima! Gunakan menu di bawah untuk mencari tempat terdekat.",
        "zh": "📍 已收到位置！使用下方選單尋找附近地點。",
        "en": "📍 Location received! Use the menu below to find nearby places.",
    }.get(user_lang, "📍 Lokasi diterima!")

    await line_api.reply_message(
        ReplyMessageRequest(
            reply_token=reply_token, messages=[TextMessage(text=message)]
        )
    )


async def handle_command(
    event: MessageEvent,
    user_id: str,
    text: str,
    reply_token: str,
    line_api: AsyncMessagingApi,
) -> None:
    """Handle slash commands"""
    cfg = get_config()

    # /lang command - change language
    lang_match = re.match(r"/lang\s+(\w+)", text.lower())
    if lang_match:
        new_lang = lang_match.group(1)
        if new_lang in ["id", "zh", "en"]:
            await db_service.set_user_language(user_id, new_lang)
            messages = {
                "id": "✅ Bahasa diubah ke Bahasa Indonesia",
                "zh": "✅ 語言已更改為繁體中文",
                "en": "✅ Language changed to English",
            }
            await line_api.reply_message(
                ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=[TextMessage(text=messages[new_lang])],
                )
            )
        else:
            await line_api.reply_message(
                ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=[
                        TextMessage(
                            text="Invalid language. Use: /lang id, /lang zh, or /lang en"
                        )
                    ],
                )
            )
        return

    # /clear command - clear chat
    if text.lower() == "/clear":
        await db_service.clear_user_conversation(user_id)
        user_lang = await db_service.get_user_language(user_id)
        message = cfg.get_message("cleared")
        await line_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token, messages=[TextMessage(text=message)]
            )
        )
        return

    # /help command - show help
    if text.lower() in ["/help", "help"]:
        user_lang = await db_service.get_user_language(user_id)
        message = cfg.get_message("help")
        await line_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token, messages=[TextMessage(text=message)]
            )
        )
        return

    # Unknown command
    user_lang = await db_service.get_user_language(user_id)
    message = cfg.get_message("unknown_command")
    await line_api.reply_message(
        ReplyMessageRequest(
            reply_token=reply_token, messages=[TextMessage(text=message)]
        )
    )


async def handle_postback(event: PostbackEvent) -> None:
    """Handle postback events from Rich Menu"""
    user_id = event.source.user_id
    reply_token = event.reply_token
    postback_data = event.postback.data

    # Handle with postback handler
    await postback_handler.handle_postback(
        reply_token, user_id, postback_data, user_location=None
    )


@app.post("/webhook")
async def webhook(request: Request):
    """LINE webhook endpoint"""
    _, parser = get_line_api()

    signature = request.headers.get("X-Line-Signature", "")
    body = (await request.body()).decode()

    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    for event in events:
        try:
            if isinstance(event, MessageEvent):
                if isinstance(event.message, TextMessageContent):
                    await handle_text_message(event)
                elif isinstance(event.message, LocationMessageContent):
                    await handle_location_message(event)
            elif isinstance(event, PostbackEvent):
                await handle_postback(event)
        except Exception as e:
            log.error(f"Error handling event: {e}", exc_info=True)

    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
