"""
IMIGO - Indonesian Migrant Worker Assistant
AI-powered LINE bot with seamless multilingual support
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    AsyncMessagingApi,
    MarkMessagesAsReadByTokenRequest,
    ReplyMessageRequest,
    TextMessage,
    FlexMessage,
    FlexContainer,
    QuickReply,
    QuickReplyItem,
    MessageAction,
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    PostbackEvent,
)

from config import load_config, get_config, NEW_USER_WELCOME_MESSAGE
from dependencies import (
    initialize_services,
    cleanup_services,
    get_database_service,
    get_ai_service,
    get_translation_service,
    get_language_detection_service,
    get_rich_menu_service,
    get_line_messaging_api,
    get_line_parser,
)
from services.flex_messages import (
    create_new_user_welcome_flex,
    create_help_flex_message,
    create_emergency_flex_message,
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    cfg = load_config()
    await initialize_services()
    log.info(f"{cfg.name} started with default language: {cfg.language}")

    try:
        yield
    finally:
        # Shutdown
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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Line-Signature"],
)

# Include API routers
from api.routes import chat, translation, system, rich_menu

app.include_router(chat.router)
app.include_router(translation.router)
app.include_router(system.router)
app.include_router(rich_menu.router)


@app.get("/")
async def root():
    """Root endpoint"""
    cfg = get_config()
    return {
        "status": "running",
        "bot": cfg.name,
        "default_language": cfg.language,
        "country": cfg.country,
        "version": "2.0.0",
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


async def detect_and_update_language(
    user_id: str, text: str, db_service, language_detection_service, rich_menu_service
) -> str:
    """
    Get user's language preference or None for new users.

    For existing users, language preference is sticky and only changed
    via explicit /lang command or rich menu selection.

    For new users, returns None to prompt them to select a language.
    """
    # Get current user language
    current_lang = await db_service.get_user_language(user_id)

    # For existing users, use their saved preference
    if current_lang:
        return current_lang

    # New user - return None to prompt language selection
    log.info(f"New user {user_id[:8]}: prompting for language selection")
    return None


async def handle_text_message(event: MessageEvent, user_id: str, text: str) -> None:
    """Handle text messages from users with seamless multilingual support"""
    cfg = get_config()

    # Get services
    line_api = await get_line_messaging_api()
    db_service = await get_database_service()
    ai_service = await get_ai_service()
    translation_service = await get_translation_service()
    language_detection_service = await get_language_detection_service()
    rich_menu_service = await get_rich_menu_service()

    # Mark message as read (with error handling)
    try:
        if hasattr(event.message, 'mark_as_read_token') and event.message.mark_as_read_token:
            await line_api.mark_messages_as_read_by_token(
                mark_messages_as_read_by_token_request=MarkMessagesAsReadByTokenRequest(
                    markAsReadToken=event.message.mark_as_read_token
                ),
            )
    except Exception as e:
        log.warning(f"Failed to mark message as read: {e}")

    # Get user's language preference (None for new users)
    user_lang = await detect_and_update_language(
        user_id, text, db_service, language_detection_service, rich_menu_service
    )

    # Handle new users - prompt for language selection
    if user_lang is None:
        # Show beautiful flex message with language selection buttons
        flex_content = create_new_user_welcome_flex()
        await line_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    FlexMessage(
                        alt_text="Welcome to IMIGO! Please select your language.",
                        contents=FlexContainer.from_dict(flex_content)
                    )
                ],
            )
        )
        return

    # Check if user is explicitly requesting language change via command
    if text.strip().lower().startswith("/lang"):
        parts = text.strip().split()
        if len(parts) == 2:
            lang_code = parts[1].lower()
            if cfg.is_valid_language(lang_code):
                # Check if this is a first-time language selection
                is_new_user = user_lang is None

                await db_service.set_user_language(user_id, lang_code)
                await rich_menu_service.set_user_rich_menu(user_id, lang_code)
                log.info(f"User {user_id[:8]} {'set initial' if is_new_user else 'changed'} language to {lang_code}")

                # Send welcome message for new users, confirmation for existing users
                if is_new_user:
                    message_text = cfg.get_message("welcome", lang_code)
                else:
                    message_text = cfg.get_message("language_changed", lang_code)

                await line_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=message_text)],
                    )
                )
                return

        # Show language selection with quick reply buttons
        quick_reply = QuickReply(
            items=[
                QuickReplyItem(action=MessageAction(label="🇮🇩 Bahasa Indonesia", text="/lang id")),
                QuickReplyItem(action=MessageAction(label="🇹🇼 繁體中文", text="/lang zh")),
                QuickReplyItem(action=MessageAction(label="🇬🇧 English", text="/lang en")),
                QuickReplyItem(action=MessageAction(label="🇻🇳 Tiếng Việt", text="/lang vi")),
            ]
        )
        await line_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(
                        text=cfg.get_message("language_select", user_lang),
                        quick_reply=quick_reply,
                    )
                ],
            )
        )
        return

    # Handle other simple commands
    if text.strip().lower() == "/help":
        # Show help menu with flex message
        flex_content = create_help_flex_message(user_lang)
        await line_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    FlexMessage(
                        alt_text="IMIGO Help Menu - Select a category",
                        contents=FlexContainer.from_dict(flex_content)
                    )
                ],
            )
        )
        return

    if text.strip().lower() == "/emergency":
        # Show emergency contacts with flex message
        flex_content = create_emergency_flex_message(user_lang)
        await line_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    FlexMessage(
                        alt_text="Emergency Contacts - Taiwan",
                        contents=FlexContainer.from_dict(flex_content)
                    )
                ],
            )
        )
        return

    if text.strip().lower() == "/clear":
        await db_service.clear_user_conversation(user_id)
        await line_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=cfg.get_message("cleared", user_lang))],
            )
        )
        return

    # Handle group chat translation
    group_id = getattr(event.source, "group_id", None)
    if group_id:
        group_settings = await db_service.get_group_settings(group_id)
        if group_settings and group_settings.get("translate_enabled"):
            target_lang = group_settings.get("target_language", "zh")
            try:
                translated = await translation_service.translate_message(
                    text, target_lang, source_language="auto"
                )
                formatted = translation_service.format_translation_message(
                    text, translated, target_lang
                )
                await line_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token, messages=[TextMessage(text=formatted)]
                    )
                )
            except Exception as e:
                log.error(f"Translation error: {e}", exc_info=True)
            return

    # Use AI service for all other messages
    try:
        reply = await ai_service.generate_response(user_id, text)
    except Exception as e:
        log.error(f"AI service error: {e}", exc_info=True)
        # Fallback to help message in user's language
        reply = cfg.get_message("help", user_lang)

    await line_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token, messages=[TextMessage(text=reply)]
        )
    )


async def handle_postback(event: PostbackEvent) -> None:
    """Handle postback events from rich menu buttons"""
    cfg = get_config()

    # Get services
    line_api = await get_line_messaging_api()
    db_service = await get_database_service()
    ai_service = await get_ai_service()
    rich_menu_service = await get_rich_menu_service()

    user_id = event.source.user_id
    data = event.postback.data

    log.info(f"Postback event: {data} from user {user_id[:8]}")

    # Get user language
    user_lang = await db_service.get_user_language(user_id) or cfg.language

    if data == "clear_chat":
        await db_service.clear_user_conversation(user_id)
        await line_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=cfg.get_message("cleared", user_lang))],
            )
        )

    elif data == "category_emergency":
        # Show emergency contacts with flex message
        flex_content = create_emergency_flex_message(user_lang)
        await line_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    FlexMessage(
                        alt_text="Emergency Contacts - Taiwan",
                        contents=FlexContainer.from_dict(flex_content)
                    )
                ],
            )
        )

    elif data == "category_language":
        # Show language selection with quick reply buttons
        quick_reply = QuickReply(
            items=[
                QuickReplyItem(action=MessageAction(label="🇮🇩 Bahasa Indonesia", text="/lang id")),
                QuickReplyItem(action=MessageAction(label="🇹🇼 繁體中文", text="/lang zh")),
                QuickReplyItem(action=MessageAction(label="🇬🇧 English", text="/lang en")),
                QuickReplyItem(action=MessageAction(label="🇻🇳 Tiếng Việt", text="/lang vi")),
            ]
        )
        await line_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(
                        text=cfg.get_message("language_select", user_lang),
                        quick_reply=quick_reply,
                    )
                ],
            )
        )

    elif data.startswith("lang_"):
        # Handle language switching via postback
        lang_code = data.split("_")[1]
        if cfg.is_valid_language(lang_code):
            # Check if this is a first-time language selection
            current_lang = await db_service.get_user_language(user_id)
            is_new_user = current_lang is None

            await db_service.set_user_language(user_id, lang_code)
            await rich_menu_service.set_user_rich_menu(user_id, lang_code)
            log.info(f"User {user_id[:8]} {'set initial' if is_new_user else 'changed'} language to {lang_code} via postback")

            # Send welcome message for new users, confirmation for existing users
            if is_new_user:
                message_text = cfg.get_message("welcome", lang_code)
            else:
                message_text = cfg.get_message("language_changed", lang_code)

            await line_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=message_text)],
                )
            )

    else:
        # Handle category postbacks with AI
        prompts = {
            "category_labor": "I have a problem at work",
            "category_government": "I need information about government services",
            "category_daily": "I need help with daily life",
            "category_translate": "I need translation help",
            "category_healthcare": "I need healthcare information",
        }

        prompt = prompts.get(data, cfg.get_message("help", user_lang))

        try:
            reply = await ai_service.generate_response(user_id, prompt)
        except Exception as e:
            log.error(f"AI service error in postback: {e}", exc_info=True)
            reply = cfg.get_message("help", user_lang)

        await line_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token, messages=[TextMessage(text=reply)]
            )
        )


async def handle_message(event: MessageEvent) -> None:
    """Route message events to appropriate handlers"""
    user_id = event.source.user_id

    if isinstance(event.message, TextMessageContent):
        await handle_text_message(event, user_id, event.message.text)
    else:
        log.info(f"Unhandled message type: {type(event.message)}")


@app.post("/webhook")
async def webhook(request: Request):
    """LINE webhook endpoint for receiving events"""
    try:
        parser = get_line_parser()

        # Get signature and body
        signature = request.headers.get("X-Line-Signature", "")
        body = (await request.body()).decode()

        # Validate signature and parse events
        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            log.error("Invalid LINE signature")
            raise HTTPException(status_code=400, detail="Invalid signature")

        # Process each event
        for event in events:
            try:
                if isinstance(event, MessageEvent):
                    await handle_message(event)
                elif isinstance(event, PostbackEvent):
                    await handle_postback(event)
                else:
                    log.info(f"Unhandled event type: {type(event).__name__}")
            except Exception as e:
                # Log error but don't fail the webhook
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
