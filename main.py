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
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    PostbackEvent,
)

from database.database import DatabaseService
from services.ai_service import AIService
from services.translation_service import TranslationService
from config import load_config, get_config

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

db_service: DatabaseService
ai_service: AIService
translation_service: TranslationService

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
    global db_service, ai_service, translation_service
    global line_async_client, line_messaging_api, line_parser

    cfg = load_config()

    # database
    db_service = DatabaseService()
    await db_service.init_db()

    # AI and translation
    ai_service = AIService(db_service, cfg)
    translation_service = TranslationService(cfg)

    line_config = Configuration(access_token=cfg.line_token)
    line_async_client = AsyncApiClient(line_config)
    line_messaging_api = AsyncMessagingApi(line_async_client)
    line_parser = WebhookParser(cfg.line_secret)

    log.info(f"{cfg.bot.name} started ({cfg.bot.language})")

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
from api.routes import chat, translation, system

app.include_router(chat.router)
app.include_router(translation.router)
app.include_router(system.router)


def get_line_api():
    return line_messaging_api, line_parser


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


async def handle_text_message(event: MessageEvent, user_id: str, text: str) -> None:
    cfg = get_config()
    line_api, _ = get_line_api()

    # Mark message as read
    await line_api.mark_messages_as_read_by_token(
        mark_messages_as_read_by_token_request=MarkMessagesAsReadByTokenRequest(
            markAsReadToken=event.message.mark_as_read_token
        ),
    )

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

    # Personal chat - use AI service
    lang = await db_service.get_user_language(user_id)
    if not lang:
        await db_service.set_user_language(user_id, cfg.bot.language)
        await line_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=cfg.get_message("welcome"))],
            )
        )
        return

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
        lang = await db_service.get_user_language(user_id)
        messages = {
            "id": "🌐 Pilih bahasa Anda:\nKetik: /lang id (Indonesia)\n/lang zh (中文)\n/lang en (English)",
            "zh": "🌐 選擇您的語言：\n輸入: /lang id (印尼文)\n/lang zh (中文)\n/lang en (英文)",
            "en": "🌐 Choose your language:\nType: /lang id (Indonesian)\n/lang zh (Chinese)\n/lang en (English)",
        }
        await line_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=messages.get(lang, messages["en"]))],
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
