import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from linebot.v3.webhook import WebhookParser
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    AsyncApiClient,
    AsyncMessagingApi,
    MarkMessagesAsReadByTokenRequest,
    ReplyMessageRequest,
    TextMessage,
    QuickReply,
    QuickReplyItem,
    MessageAction,
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    PostbackEvent,
)

from database.database import DatabaseService
from services.ai_service import AIService
from services.translation_service import TranslationService
from services.language_detection import LanguageDetectionService
from services.intent_service import IntentService, Intent
from config import load_config, get_config

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

db_service: DatabaseService
ai_service: AIService
translation_service: TranslationService
language_detection_service: LanguageDetectionService
intent_service: IntentService

line_async_client: AsyncApiClient
line_messaging_api: AsyncMessagingApi
line_parser: WebhookParser

app = FastAPI(
    title="IMIGO - Indonesian Migrant Worker Assistant",
    description="AI-powered LINE bot and API for Indonesian migrant workers in Taiwan",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_service, ai_service, translation_service, language_detection_service, intent_service
    global line_async_client, line_messaging_api, line_parser

    cfg = load_config()

    # database
    db_service = DatabaseService()
    await db_service.init_db()

    # AI, translation, language detection, and intent detection
    ai_service = AIService(db_service, cfg)
    translation_service = TranslationService(cfg)
    language_detection_service = LanguageDetectionService(default_language=cfg.language)
    intent_service = IntentService()

    line_config = Configuration(access_token=cfg.line_token)
    line_async_client = AsyncApiClient(line_config)
    line_messaging_api = AsyncMessagingApi(line_async_client)
    line_parser = WebhookParser(cfg.line_secret)

    log.info(f"{cfg.name} started ({cfg.language})")

    try:
        yield
    finally:
        # close AI client
        await ai_service.aclose()

        # close LINE async client
        await line_async_client.close()

        # close DB
        await db_service.dispose()
        log.info("Services closed")


app.router.lifespan_context = lifespan

# Configure CORS for public API access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
from api.routes import chat, translation, system, rich_menu

app.include_router(chat.router)
app.include_router(translation.router)
app.include_router(system.router)
app.include_router(rich_menu.router)


def get_line_api():
    return line_messaging_api, line_parser


@app.get("/")
async def root():
    cfg = get_config()
    return {
        "status": "running",
        "bot": cfg.name,
        "language": cfg.language,
        "country": cfg.country,
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


async def handle_text_message(event: MessageEvent, user_id: str, text: str) -> None:
    cfg = get_config()
    line_api, _ = get_line_api()

    # Mark message as read
    await line_api.mark_messages_as_read_by_token(
        mark_messages_as_read_by_token_request=MarkMessagesAsReadByTokenRequest(
            markAsReadToken=event.message.mark_as_read_token
        ),
    )

    # Get user language
    user_lang = await db_service.get_user_language(user_id) or cfg.language

    # Detect intent
    intent = intent_service.detect_intent(text)
    log.info(f"User {user_id[:8]} intent: {intent}")

    # Handle commands
    if intent == Intent.COMMAND:
        command, args = intent_service.extract_command(text)

        if command == "lang":
            if args and cfg.is_valid_language(args):
                await db_service.set_user_language(user_id, args)
                log.info(f"User {user_id[:8]} changed language to {args}")
                await line_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=cfg.get_message("language_changed", args))],
                    )
                )
                return
            else:
                # Show language selection with quick reply buttons
                quick_reply = QuickReply(
                    items=[
                        QuickReplyItem(action=MessageAction(label="🇮🇩 Bahasa Indonesia", text="/lang id")),
                        QuickReplyItem(action=MessageAction(label="🇹🇼 繁體中文", text="/lang zh")),
                        QuickReplyItem(action=MessageAction(label="🇬🇧 English", text="/lang en")),
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

        elif command == "help":
            await line_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=cfg.get_message("help", user_lang))],
                )
            )
            return

        elif command == "emergency":
            await line_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=cfg.get_emergency_info())],
                )
            )
            return

        elif command == "clear":
            await db_service.clear_user_conversation(user_id)
            await line_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=cfg.get_message("cleared", user_lang))],
                )
            )
            return

    # Handle simple intents with quick responses
    if not intent_service.should_use_ai(intent):
        quick_response = intent_service.get_quick_response(intent, user_lang)
        if quick_response:
            await line_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=quick_response)],
                )
            )
            return

    # Handle emergency intent
    if intent == Intent.EMERGENCY:
        emergency_msg = cfg.get_emergency_info()
        emergency_msg += f"\n\n{cfg.get_message('help', user_lang)}"
        await line_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=emergency_msg)],
            )
        )
        return

    group_id = getattr(event.source, "group_id", None)
    if group_id:
        group_settings = await db_service.get_group_settings(group_id)
        if group_settings and group_settings.get("translate_enabled"):
            target_lang = group_settings.get("target_language", "zh")
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
            return

    # Check if this is a new user (no language set yet)
    if not await db_service.get_user_language(user_id):
        # Auto-detect language from user's first message
        detected_lang = language_detection_service.detect_language(text)
        log.info(f"New user {user_id[:8]}, detected language: {detected_lang}")
        await db_service.set_user_language(user_id, detected_lang)
        await line_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=cfg.get_message("welcome", detected_lang))],
            )
        )
        return

    # Use AI service for complex queries
    reply = await ai_service.generate_response(user_id, text)

    await line_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token, messages=[TextMessage(text=reply)]
        )
    )


async def handle_postback(event: PostbackEvent) -> None:
    cfg = get_config()
    line_api, _ = get_line_api()

    user_id = event.source.user_id
    data = event.postback.data

    log.info(f"Postback event: {data} from user {user_id[:8]}")

    if data == "clear_chat":
        await db_service.clear_user_conversation(user_id)
        await line_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=cfg.get_message("cleared"))],
            )
        )

    elif data == "category_emergency":
        emergency_info = cfg.get_emergency_info()
        await line_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=emergency_info)],
            )
        )

    elif data == "category_language":
        lang = await db_service.get_user_language(user_id) or cfg.language
        # Show language selection with quick reply buttons
        quick_reply = QuickReply(
            items=[
                QuickReplyItem(action=MessageAction(label="🇮🇩 Bahasa Indonesia", text="/lang id")),
                QuickReplyItem(action=MessageAction(label="🇹🇼 繁體中文", text="/lang zh")),
                QuickReplyItem(action=MessageAction(label="🇬🇧 English", text="/lang en")),
            ]
        )
        await line_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(
                        text=cfg.get_message("language_select", lang),
                        quick_reply=quick_reply,
                    )
                ],
            )
        )

    elif data.startswith("lang_"):
        # Handle language switching via postback (e.g., from rich menu buttons)
        lang_code = data.split("_")[1]
        if cfg.is_valid_language(lang_code):
            await db_service.set_user_language(user_id, lang_code)
            log.info(f"User {user_id[:8]} changed language to {lang_code} via postback")
            await line_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=cfg.get_message("language_changed", lang_code))],
                )
            )

    else:
        prompts = {
            "category_labor": "I have a problem at work",
            "category_government": "I need information about government services",
            "category_daily": "I need help with daily life",
            "category_translate": "I need translation help",
            "category_healthcare": "I need healthcare information",
        }

        prompt = prompts.get(data, cfg.get_message("help"))
        reply = await ai_service.generate_response(user_id, prompt)

        await line_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token, messages=[TextMessage(text=reply)]
            )
        )


async def handle_message(event: MessageEvent) -> None:
    user_id = event.source.user_id

    if isinstance(event.message, TextMessageContent):
        await handle_text_message(event, user_id, event.message.text)
    else:
        log.info(f"Unhandled message type: {type(event.message)}")


@app.post("/webhook")
async def webhook(request: Request):
    _, parser = get_line_api()

    signature = request.headers.get("X-Line-Signature", "")
    body = (await request.body()).decode()

    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    for event in events:
        if isinstance(event, MessageEvent):
            await handle_message(event)
        elif isinstance(event, PostbackEvent):
            await handle_postback(event)

    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
