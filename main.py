import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    AsyncMessagingApi,
    FlexContainer,
    FlexMessage,
    MarkMessagesAsReadByTokenRequest,
    MessageAction,
    QuickReply,
    QuickReplyItem,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import (
    FollowEvent,
    MessageEvent,
    PostbackEvent,
    TextMessageContent,
)

from api.routes import chat, rich_menu, system, translation
from config import get_config, load_config
from database.database import DatabaseService
from dependencies import (
    cleanup_services,
    get_ai_service,
    get_database_service,
    get_line_messaging_api,
    get_line_parser,
    get_rich_menu_service,
    get_translation_service,
    initialize_services,
)
from services.flex_messages import (
    create_emergency_flex_message,
    create_help_flex_message,
    create_new_user_welcome_flex,
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    cfg = load_config()
    await initialize_services()
    log.info(f"{cfg.name} started with default language: {cfg.language}")
    try:
        yield
    finally:
        await cleanup_services()
        log.info("Services closed")


app = FastAPI(
    title="IMIGO - Indonesian Migrant Worker Assistant",
    description="AI-powered LINE bot and API for Indonesian migrant workers in Taiwan",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(chat.router)
app.include_router(translation.router)
app.include_router(system.router)
app.include_router(rich_menu.router)


@app.get("/")
async def root() -> dict[str, Any]:
    cfg = get_config()
    return {
        "status": "running",
        "bot": cfg.name,
        "default_language": cfg.language,
        "country": cfg.country,
        "version": "2.0.0",
    }


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy"}


async def get_user_language(user_id: str, db_service: DatabaseService) -> Optional[str]:
    current_lang = await db_service.get_user_language(user_id)
    if not current_lang:
        log.info(f"New user {user_id[:8]}: prompting for language selection")
    return current_lang


def create_language_quick_reply() -> QuickReply:
    return QuickReply(
        items=[
            QuickReplyItem(action=MessageAction(label="🇮🇩 Bahasa Indonesia", text="/lang id")),
            QuickReplyItem(action=MessageAction(label="🇹🇼 繁體中文", text="/lang zh")),
            QuickReplyItem(action=MessageAction(label="🇬🇧 English", text="/lang en")),
            QuickReplyItem(action=MessageAction(label="🇻🇳 Tiếng Việt", text="/lang vi")),
        ]
    )


async def send_flex_message(line_api: AsyncMessagingApi, reply_token: str, flex_content: dict, alt_text: str) -> None:
    await line_api.reply_message(
        ReplyMessageRequest(
            reply_token=reply_token,
            messages=[FlexMessage(alt_text=alt_text, contents=FlexContainer.from_dict(flex_content))],
        )
    )


async def send_text_message(line_api: AsyncMessagingApi, reply_token: str, text: str, quick_reply: Optional[QuickReply] = None) -> None:
    await line_api.reply_message(
        ReplyMessageRequest(
            reply_token=reply_token,
            messages=[TextMessage(text=text, quick_reply=quick_reply)],
        )
    )


async def set_user_language(user_id: str, lang_code: str, db_service: DatabaseService, rich_menu_service) -> tuple[bool, str]:
    current_lang = await db_service.get_user_language(user_id)
    is_new_user = current_lang is None

    await db_service.set_user_language(user_id, lang_code)
    await rich_menu_service.set_user_rich_menu(user_id, lang_code)

    log.info(f"User {user_id[:8]} {'set initial' if is_new_user else 'changed'} language to {lang_code}")

    cfg = get_config()
    message = cfg.get_message("welcome" if is_new_user else "language_changed", lang_code)
    return is_new_user, message


async def handle_text_message(event: MessageEvent, user_id: str, text: str) -> None:
    cfg = get_config()
    line_api = await get_line_messaging_api()
    db_service = await get_database_service()
    ai_service = await get_ai_service()
    translation_service = await get_translation_service()
    rich_menu_service = await get_rich_menu_service()

    try:
        if hasattr(event.message, "mark_as_read_token") and event.message.mark_as_read_token:
            await line_api.mark_messages_as_read_by_token(
                MarkMessagesAsReadByTokenRequest(markAsReadToken=event.message.mark_as_read_token)
            )
    except Exception as e:
        log.warning(f"Failed to mark message as read: {e}")

    cmd = text.strip().lower()

    # Check if text is a language name - usability enhancement
    lang_map = {
        "bahasa indonesia": "id",
        "indonesia": "id",
        "indonesian": "id",
        "中文": "zh",
        "繁體中文": "zh",
        "chinese": "zh",
        "english": "en",
        "tiếng việt": "vi",
        "vietnamese": "vi",
        "vietnam": "vi"
    }
    if cmd in lang_map:
        text = f"/lang {lang_map[cmd]}"
        cmd = text.strip().lower()

    # Handle language selection first (works for both new and existing users)
    if cmd.startswith("/lang"):
        parts = text.strip().split()
        if len(parts) == 2 and cfg.is_valid_language(parts[1].lower()):
            _, message = await set_user_language(user_id, parts[1].lower(), db_service, rich_menu_service)
            await send_text_message(line_api, event.reply_token, message)
            return
        # Show language selection prompt
        user_lang = await get_user_language(user_id, db_service)
        await send_text_message(line_api, event.reply_token, cfg.get_message("language_select", user_lang or cfg.language), create_language_quick_reply())
        return

    user_lang = await get_user_language(user_id, db_service)

    if user_lang is None:
        await send_flex_message(line_api, event.reply_token, create_new_user_welcome_flex(), "Welcome to IMIGO! Please select your language.")
        return

    if cmd == "/help":
        await send_flex_message(line_api, event.reply_token, create_help_flex_message(user_lang), "IMIGO Help Menu")
        return

    if cmd == "/emergency":
        await send_flex_message(line_api, event.reply_token, create_emergency_flex_message(user_lang), "Emergency Contacts - Taiwan")
        return

    if cmd == "/clear":
        await db_service.clear_user_conversation(user_id)
        await send_text_message(line_api, event.reply_token, cfg.get_message("cleared", user_lang))
        return

    group_id = getattr(event.source, "group_id", None)
    if group_id:
        group_settings = await db_service.get_group_settings(group_id)
        if group_settings and group_settings.get("translate_enabled"):
            try:
                translated = await translation_service.translate_message(text, group_settings.get("target_language", "zh"), source_language="auto")
                await send_text_message(line_api, event.reply_token, translation_service.format_translation_message(text, translated, group_settings.get("target_language", "zh")))
            except Exception as e:
                log.error(f"Translation error: {e}", exc_info=True)
            return

    try:
        reply = await ai_service.generate_response(user_id, text)
    except Exception as e:
        log.error(f"AI service error: {e}", exc_info=True)
        reply = cfg.get_message("help", user_lang)

    await send_text_message(line_api, event.reply_token, reply)


async def handle_postback(event: PostbackEvent) -> None:
    cfg = get_config()
    line_api = await get_line_messaging_api()
    db_service = await get_database_service()
    ai_service = await get_ai_service()
    rich_menu_service = await get_rich_menu_service()

    user_id = event.source.user_id
    data = event.postback.data
    log.info(f"Postback event: {data} from user {user_id[:8]}")

    user_lang = await db_service.get_user_language(user_id) or cfg.language

    if data == "clear_chat":
        await db_service.clear_user_conversation(user_id)
        await send_text_message(line_api, event.reply_token, cfg.get_message("cleared", user_lang))

    elif data == "category_emergency":
        await send_flex_message(line_api, event.reply_token, create_emergency_flex_message(user_lang), "Emergency Contacts - Taiwan")

    elif data == "category_language":
        await send_text_message(line_api, event.reply_token, cfg.get_message("language_select", user_lang), create_language_quick_reply())

    elif data.startswith("lang_"):
        lang_code = data.split("_")[1]
        if cfg.is_valid_language(lang_code):
            _, message = await set_user_language(user_id, lang_code, db_service, rich_menu_service)
            await send_text_message(line_api, event.reply_token, message)

    else:
        prompts = {
            "category_labor": "I have a problem at work",
            "category_government": "I need information about government services",
            "category_daily": "I need help with daily life",
            "category_translate": "I need translation help",
            "category_healthcare": "I need healthcare information",
        }

        try:
            reply = await ai_service.generate_response(user_id, prompts.get(data, cfg.get_message("help", user_lang)))
        except Exception as e:
            log.error(f"AI service error in postback: {e}", exc_info=True)
            reply = cfg.get_message("help", user_lang)

        await send_text_message(line_api, event.reply_token, reply)


async def handle_follow(event: FollowEvent) -> None:
    """Handle when a user adds the bot as a friend"""
    user_id = event.source.user_id
    log.info(f"New user followed: {user_id[:8]}")

    line_api = await get_line_messaging_api()
    db_service = await get_database_service()
    rich_menu_service = await get_rich_menu_service()

    # Check if user already exists (e.g., they blocked and unblocked)
    existing_lang = await db_service.get_user_language(user_id)

    if existing_lang:
        # Returning user - send a welcome back message in their language
        cfg = get_config()
        await send_text_message(line_api, event.reply_token, cfg.get_message("welcome", existing_lang))
        await rich_menu_service.set_user_rich_menu(user_id, existing_lang)
    else:
        # Brand new user - send multi-language welcome flex message
        await send_flex_message(line_api, event.reply_token, create_new_user_welcome_flex(), "Welcome to IMIGO! Please select your language.")


async def handle_message(event: MessageEvent) -> None:
    if isinstance(event.message, TextMessageContent):
        await handle_text_message(event, event.source.user_id, event.message.text)
    else:
        log.info(f"Unhandled message type: {type(event.message)}")


@app.post("/webhook")
async def webhook(request: Request) -> dict[str, str]:
    try:
        signature = request.headers.get("X-Line-Signature", "")
        body = (await request.body()).decode()

        try:
            events = get_line_parser().parse(body, signature)
        except InvalidSignatureError:
            log.error("Invalid LINE signature")
            raise HTTPException(status_code=400, detail="Invalid signature")

        for event in events:
            try:
                if isinstance(event, FollowEvent):
                    await handle_follow(event)
                elif isinstance(event, MessageEvent):
                    await handle_message(event)
                elif isinstance(event, PostbackEvent):
                    await handle_postback(event)
                else:
                    log.info(f"Unhandled event type: {type(event).__name__}")
            except Exception as e:
                log.error(f"Error processing event: {e}", exc_info=True)

        return {"status": "ok"}

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Webhook error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
