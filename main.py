from __future__ import annotations

import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv

from linebot.v3.webhook import WebhookParser
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    AsyncApiClient,
    AsyncMessagingApi,
    ReplyMessageRequest,
    TextMessage,
    QuickReply,
    QuickReplyItem,
    PostbackAction,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent, PostbackEvent

from database.database import DatabaseService
from services.ai_service import AIService

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

load_dotenv()
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
CHANNEL_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
if not CHANNEL_SECRET or not CHANNEL_TOKEN:
    raise RuntimeError("Missing LINE credentials")

SUPPORTED_LANGUAGES = ["en", "zh", "id", "vi", "th", "fil", "my", "km"]
LANG_NATIVE = {
    "en": "English",
    "zh": "中文",
    "id": "Bahasa Indonesia",
    "vi": "Tiếng Việt",
    "th": "ไทย",
    "fil": "Filipino",
    "my": "မြန်မာ",
    "km": "ខ្មែរ",
}

I18N = {
    "en": {
        "help": "Commands: /help, /clear, /stats, /lang <code>, /languages, /mylang",
        "choose_language": "Choose your language:",
        "unknown_command": "Unknown command",
        "category_selected": "📋 {category} category selected. Ask me about {category}.",
        "conversation_cleared": "✅ Conversation cleared",
        "stats_header": "📊 Stats",
        "stats_user": "Your messages: {n}",
        "stats_ai": "My responses: {n}",
        "stats_total": "Total: {n}",
        "available_languages": "Available languages:",
    },
    "zh": {
        "help": "指令：/help, /clear, /stats, /lang <代碼>, /languages, /mylang",
        "choose_language": "請選擇語言：",
        "unknown_command": "指令無效",
        "category_selected": "📋 已選 {category} 類別。可以詢問 {category} 相關問題。",
        "conversation_cleared": "✅ 對話已清除",
        "stats_header": "📊 統計",
        "stats_user": "你的訊息：{n}",
        "stats_ai": "我的回覆：{n}",
        "stats_total": "總計：{n}",
        "available_languages": "可用語言：",
    },
    "id": {
        "help": "Perintah: /help, /clear, /stats, /lang <kode>, /languages, /mylang",
        "choose_language": "Pilih bahasa:",
        "unknown_command": "Perintah tidak dikenali",
        "category_selected": "📋 Kategori {category} dipilih. Tanyakan tentang {category}.",
        "conversation_cleared": "✅ Percakapan dihapus",
        "stats_header": "📊 Statistik",
        "stats_user": "Pesan Anda: {n}",
        "stats_ai": "Balasan saya: {n}",
        "stats_total": "Total: {n}",
        "available_languages": "Bahasa yang tersedia:",
    },
    "vi": {
        "help": "Lệnh: /help, /clear, /stats, /lang <mã>, /languages, /mylang",
        "choose_language": "Chọn ngôn ngữ:",
        "unknown_command": "Lệnh không hợp lệ",
        "category_selected": "📋 Đã chọn mục {category}. Hãy hỏi về {category}.",
        "conversation_cleared": "✅ Đã xóa cuộc trò chuyện",
        "stats_header": "📊 Thống kê",
        "stats_user": "Tin nhắn của bạn: {n}",
        "stats_ai": "Phản hồi của tôi: {n}",
        "stats_total": "Tổng: {n}",
        "available_languages": "Ngôn ngữ khả dụng:",
    },
    "th": {
        "help": "คำสั่ง: /help, /clear, /stats, /lang <รหัส>, /languages, /mylang",
        "choose_language": "เลือกภาษา:",
        "unknown_command": "คำสั่งไม่ถูกต้อง",
        "category_selected": "📋 เลือกหมวด {category} แล้ว ถามเกี่ยวกับ {category} ได้",
        "conversation_cleared": "✅ ล้างการสนทนาแล้ว",
        "stats_header": "📊 สถิติ",
        "stats_user": "ข้อความของคุณ: {n}",
        "stats_ai": "การตอบของฉัน: {n}",
        "stats_total": "รวม: {n}",
        "available_languages": "ภาษาที่มี:",
    },
    "fil": {
        "help": "Mga utos: /help, /clear, /stats, /lang <code>, /languages, /mylang",
        "choose_language": "Piliin ang wika:",
        "unknown_command": "Hindi kilalang utos",
        "category_selected": "📋 Napiling {category}. Magtanong tungkol sa {category}.",
        "conversation_cleared": "✅ Nalinaw na ang pag-uusap",
        "stats_header": "📊 Estadistika",
        "stats_user": "Iyong mensahe: {n}",
        "stats_ai": "Aking tugon: {n}",
        "stats_total": "Kabuuan: {n}",
        "available_languages": "Magagamit na wika:",
    },
    "my": {
        "help": "အမိန့်များ: /help, /clear, /stats, /lang <code>, /languages, /mylang",
        "choose_language": "ဘာသာစကားရွေးပါ:",
        "unknown_command": "မသိရှိသော အမိန့်",
        "category_selected": "📋 {category} အမျိုးအစားကို ရွေးထားသည်။ {category} အကြောင်း မေးပါ။",
        "conversation_cleared": "✅ စကားဝိုင်းရှင်းလင်းပြီး",
        "stats_header": "📊 စာရင်းاحاح",
        "stats_user": "သင့်မက်ဆေ့ချ်များ: {n}",
        "stats_ai": "ငါ့ပြန်လည်ဖြေကြားမှု: {n}",
        "stats_total": "စုစုပေါင်း: {n}",
        "available_languages": "ရရှိနိုင်သောဘာသာများ:",
    },
    "km": {
        "help": "ពាក្យបញ្ជា៖ /help, /clear, /stats, /lang <កូដ>, /languages, /mylang",
        "choose_language": "ជ្រើសរើសភាសា៖",
        "unknown_command": "ពាក្យបញ្ជាមិនត្រឹមត្រូវ",
        "category_selected": "📋 បានជ្រើសប្រភេទ {category}។ សួរអំពី {category}។",
        "conversation_cleared": "✅ ការសន្ទនាត្រូវបានលុប",
        "stats_header": "📊 ស្ថិតិ",
        "stats_user": "សាររបស់អ្នក៖ {n}",
        "stats_ai": "ការឆ្លើយតបរបស់ខ្ញុំ៖ {n}",
        "stats_total": "សរុប៖ {n}",
        "available_languages": "ភាសាដែលមាន៖",
    },
}


def t(lang: str, key: str, **kw) -> str:
    base = I18N.get(lang) or I18N["en"]
    s = base.get(key) or I18N["en"].get(key, key)
    return s.format(**kw)


db_service: DatabaseService
ai_service: AIService

app = FastAPI(title="Migrant Worker Bot")


@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_service, ai_service
    db_service = DatabaseService()
    await db_service.init_db()
    ai_service = AIService(db_service)
    yield
    await db_service.dispose()


app.router.lifespan_context = lifespan  # FastAPI 0.110+ compatible

config = Configuration(access_token=CHANNEL_TOKEN)
async_client = AsyncApiClient(config)
line_api = AsyncMessagingApi(async_client)
parser = WebhookParser(CHANNEL_SECRET)


def _lang_quick_reply() -> QuickReply:
    return QuickReply(
        items=[
            QuickReplyItem(action=PostbackAction(label="🇺🇸 English", data="lang_en")),
            QuickReplyItem(action=PostbackAction(label="🇹🇼 中文", data="lang_zh")),
            QuickReplyItem(action=PostbackAction(label="🇮🇩 Indonesia", data="lang_id")),
            QuickReplyItem(action=PostbackAction(label="🇻🇳 Việt Nam", data="lang_vi")),
            QuickReplyItem(action=PostbackAction(label="🇹🇭 ไทย", data="lang_th")),
            QuickReplyItem(action=PostbackAction(label="🇵🇭 Filipino", data="lang_fil")),
            QuickReplyItem(action=PostbackAction(label="🇲🇲 မြန်မာ", data="lang_my")),
            QuickReplyItem(action=PostbackAction(label="🇰🇭 ខ្មែរ", data="lang_km")),
        ]
    )


def _languages_list_msg(lang: str) -> str:
    head = t(lang, "available_languages")
    lines = [f"- {code}: {LANG_NATIVE[code]}" for code in SUPPORTED_LANGUAGES]
    return head + "\n" + "\n".join(lines)


@app.get("/")
async def root():
    return {
        "message": "Migrant Worker Bot",
        "status": "running",
        "services": {"ai": True, "db": True},
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "ai": "enabled",
        "db": "enabled",
        "languages": SUPPORTED_LANGUAGES,
    }


# ---------- Command routing ----------


async def handle_command(user_id: str, cmd_raw: str, lang: str) -> str:
    cmd = cmd_raw.lower().strip()
    if cmd == "/help":
        return t(lang, "help")
    if cmd.startswith("/lang "):
        code = cmd[6:].strip()
        return await ai_service.set_user_language(user_id, code)
    if cmd == "/languages":
        return _languages_list_msg(lang)
    if cmd == "/mylang":
        return await ai_service.get_user_language_info(user_id)
    if cmd == "/clear":
        await ai_service.clear_conversation(user_id)
        return t(lang, "conversation_cleared")
    if cmd == "/stats":
        hist = await db_service.get_conversation_history(user_id, limit=100)
        u = sum(1 for m in hist if m["role"] == "user")
        a = sum(1 for m in hist if m["role"] == "assistant")
        return "\n".join(
            [
                t(lang, "stats_header"),
                t(lang, "stats_user", n=u),
                t(lang, "stats_ai", n=a),
                t(lang, "stats_total", n=len(hist)),
            ]
        )
    return t(lang, "unknown_command")


# ---------- Reply helpers ----------


async def reply_text(event, text: str) -> None:
    await line_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token, messages=[TextMessage(text=text)]
        )
    )


# ---------- Event handlers ----------


async def on_message_event(event: MessageEvent) -> None:
    if not isinstance(event.message, TextMessageContent):
        return
    user_id = event.source.user_id
    user_lang = await db_service.get_user_language(user_id)
    text = event.message.text
    if text.startswith("/"):
        reply = await handle_command(user_id, text, user_lang)
    else:
        reply = await ai_service.generate_response(
            user_id, text
        )  # should honor user_lang internally
    await reply_text(event, reply)


async def on_postback_event(event: PostbackEvent) -> None:
    user_id = event.source.user_id
    user_lang = await db_service.get_user_language(user_id)
    data = event.postback.data

    if data.startswith("lang_"):
        code = data[5:]
        msg = await ai_service.set_user_language(user_id, code)
        await reply_text(event, msg)
        return

    if data.startswith("category_"):
        category = data[9:]
        if category == "language":
            await line_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(
                            text=t(user_lang, "choose_language"),
                            quick_reply=_lang_quick_reply(),
                        )
                    ],
                )
            )
        else:
            await reply_text(
                event, t(user_lang, "category_selected", category=category.title())
            )
        return

    if data == "clear_chat":
        await ai_service.clear_conversation(user_id)
        await reply_text(event, t(user_lang, "conversation_cleared"))
        return


# ---------- Webhook endpoint ----------


@app.post("/webhook")
async def webhook(request: Request):
    signature = request.headers.get("X-Line-Signature", "")
    body = (await request.body()).decode()
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    for ev in events:
        if isinstance(ev, MessageEvent):
            await on_message_event(ev)
        elif isinstance(ev, PostbackEvent):
            await on_postback_event(ev)
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
