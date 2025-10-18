import logging
from contextlib import asynccontextmanager

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
from linebot.v3.webhooks import MessageEvent, TextMessageContent

from database.database import DatabaseService
from services.ai_service import AIService
from config import load_config, get_config

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

db_service: DatabaseService
ai_service: AIService

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_service, ai_service

    cfg = load_config()

    db_service = DatabaseService()
    await db_service.init_db()
    ai_service = AIService(db_service, cfg)

    log.info(f"{cfg.bot.name} started ({cfg.bot.language})")
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


async def handle_message(event: MessageEvent) -> None:
    if not isinstance(event.message, TextMessageContent):
        return

    cfg = get_config()
    line_api, _ = get_line_api()

    user_id = event.source.user_id
    text = event.message.text

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

    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
