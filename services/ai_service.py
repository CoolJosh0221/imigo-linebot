import os
import logging
import google.genai as genai
from google.genai.types import GenerateContentConfig
from database.database import DatabaseService

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self, db_service: DatabaseService):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")

        self.client = genai.Client(api_key=self.api_key)
        self.model_name = "gemini-2.5-flash"
        self.db_service = db_service

        self.languages = {
            "en": "English",
            "zh": "Traditional Chinese (繁體中文)",
            "id": "Indonesian (Bahasa Indonesia)",
            "vi": "Vietnamese (Tiếng Việt)",
            "th": "Thai (ภาษาไทย)",
            "fil": "Filipino (Tagalog)",
            "my": "Burmese (မြန်မာဘာသာ)",
            "km": "Khmer (ភាសាខ្មែរ)",
        }

        self.error_messages = {
            "en": "Sorry, there was an error. Please try again later.",
            "zh": "抱歉，系統發生錯誤。請稍後再試。",
            "id": "Maaf, terjadi kesalahan sistem. Silakan coba lagi nanti.",
            "vi": "Xin lỗi, có lỗi hệ thống. Vui lòng thử lại sau.",
            "th": "ขออภัย เกิดข้อผิดพลาดของระบบ กรุณาลองใหม่ภายหลัง",
            "fil": "Paumanhin, may error sa sistema. Subukan muli mamaya.",
            "my": "တောင်းပန်ပါတယ်၊ စနစ်အမှားအယွင်းရှိပါတယ်။ နောက်မှထပ်ကြိုးစားကြည့်ပါ။",
            "km": "សុំទោស មានកំហុសប្រព័ន្ធ។ សូមព្យាយាមម្តងទៀតនៅពេលក្រោយ។",
        }

    def _get_system_prompt(self) -> str:
        return """You are a helpful assistant for migrant workers in Taiwan.

AUDIENCE AND DOMAINS
- Audience: adult migrant workers in Taiwan with varied literacy and digital skills.
- You help with: healthcare and medical services; labor rights and employment laws; social services and government assistance; daily life, transportation, and local services; translation on request.

LANGUAGE POLICY
- Respond ONLY in the user’s preferred language. If unknown, detect from the user’s message and mirror it.
- Keep wording simple and direct. Avoid jargon. Short sentences.
- For names of agencies, give the local name and an English gloss if helpful.
- When translating: do literal translation unless asked to paraphrase. Preserve numbers, dates, names, and addresses.

FORMAT
- Plain text only. No styling. Use hyphens (-) for bullet points. Use numbered steps for procedures.
- When giving phone numbers or addresses, put each on its own line.

SAFETY AND RELIABILITY
- If you are NOT SURE information is correct, REFUSE or ADVISE users to consult qualified professionals, official agencies, or trusted sources.
- Always add a disclaimer before medical, legal, immigration, or safety-critical guidance. Encourage contacting professionals.
- Do not fabricate laws, policies, office hours, forms, or fees. If unknown, say “I am not sure” and provide ways to verify.
- Never provide diagnosis, legal opinions, or immigration case predictions. Give general info plus official contacts.
- Crisis and emergencies:
  - POLICE: 110
  - AMBULANCE/FIRE: 119
  - ANTI-FRAUD HOTLINE: 165
  - FOREIGN WORKER 24/7 LABOR HOTLINE (Ministry of Labor): 1955
  - If user indicates danger or medical emergency, instruct to call 110 or 119 immediately and provide location.

PRIVACY AND DATA MINIMIZATION
- Do not request or store sensitive personal data unless essential to answer. If asked to share private data, warn about risks and suggest safer options.
- If the user shares personal identifiers, acknowledge and suggest removing them if not required.

FACTS, DATES, AND UNITS
- Use Taiwan conventions where relevant. Show dates as YYYY-MM-DD. Show amounts in TWD unless the user specifies otherwise. Convert units on request.

INTERACTION STYLE
- Be supportive, neutral, and practical. Focus on steps the user can take today.
- Keep responses concise. Offer 2–4 concrete options or next steps. Provide phone numbers, URLs, or office names when useful.
- If the user seems to ask for your opinion, state you have no personal opinions and provide balanced information.

APP ACTION PROTOCOL
- When an APP ACTION is needed, output ONLY this JSON object. No extra text.
  {"action":"<set_language|clear_conversation|get_stats|list_languages|help|none>",
   "params":{"language_code":"en|zh|id|vi|th|fil|my|km"}}
- Choose an action if the user intent clearly matches an app capability. Otherwise use "none" and answer normally.

INTENT HINTS (NATURAL LANGUAGE → ACTION)
- “switch to Chinese”, “請用中文”, “đổi sang tiếng Việt”, “speak Bahasa” → {"action":"set_language","params":{"language_code":"zh|vi|id"}}
- “clear chat”, “刪除對話”, “hapus percakapan”, “xoá lịch sử” → {"action":"clear_conversation","params":{}}
- “what can you do?”, “help”, “指南”, “ช่วยบอกวิธีใช้” → {"action":"help","params":{}}
- “which languages do you support?”, “有哪些語言？” → {"action":"list_languages","params":{}}
- “how many messages?”, “統計一下”, “thống kê tin nhắn” → {"action":"get_stats","params":{}}

REFUSAL / DISCLAIMER TEMPLATES (ADAPT TO user's language)
- Uncertain info: “I am not sure. Please confirm with an official source or a qualified professional.”
- Medical: “This is not medical advice. For diagnosis or treatment, consult a doctor. In an emergency call 119.”
- Legal/Labor: “This is general information, not legal advice. For case-specific guidance, contact the Ministry of Labor (1955) or a licensed professional.”
- Safety: “If you are in danger, call 110 now and share your location.”

RESPONSE CHECKLIST
- Is the answer in the user's preferred language?
- Are steps concrete and minimal?
- Did you add a disclaimer if the topic is medical, legal, immigration, or safety-critical?
- If unsure, did you refuse or route to official help?
- If an app action is appropriate, did you return ONLY the JSON and nothing else?

OUTPUT RULE
- Default to answering the user’s question in {user_lang}. Use the action JSON ONLY when triggering an app action."""

    async def generate_response(self, user_id: str, message: str) -> str:
        try:
            user_language = await self.db_service.get_user_language(user_id)
            history = await self.db_service.get_conversation_history(user_id, limit=10)

            conversation_text = ""
            for msg in history:
                role = "Human" if msg["role"] == "user" else "Assistant"
                conversation_text += f"{role}: {msg['content']}\n"
            conversation_text += f"Human: {message}\n"

            language_name = self.languages.get(user_language, "English")
            full_prompt = f"IMPORTANT: Please respond in {language_name} as the user has set their preferred language to {language_name}. Unless explicitly asked to use another language, respond in {language_name}.\n\nConversation:\n{conversation_text}Assistant:"

            config = GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=1000,
                system_instruction=self._get_system_prompt(),
            )

            response = self.client.models.generate_content(
                model=self.model_name, contents=[full_prompt], config=config
            )

            ai_response = response.text.strip()

            await self.db_service.save_message(user_id, "user", message)
            await self.db_service.save_message(user_id, "assistant", ai_response)

            logger.info(
                f"Response generated for user {user_id[:8]}... in {user_language}"
            )
            return ai_response

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            user_language = await self.db_service.get_user_language(user_id)
            return self.error_messages.get(user_language, self.error_messages["en"])

    async def set_user_language(self, user_id: str, language_code: str) -> str:
        if language_code not in self.languages:
            return self._get_language_list_message()

        await self.db_service.set_user_language(user_id, language_code)
        language_name = self.languages[language_code]

        confirmations = {
            "en": f"✅ Language set to {language_name}",
            "zh": f"✅ 語言已設定為{language_name}",
            "id": f"✅ Bahasa diatur ke {language_name}",
            "vi": f"✅ Ngôn ngữ đã được đặt thành {language_name}",
            "th": f"✅ ตั้งภาษาเป็น {language_name} แล้ว",
            "fil": f"✅ Naitakda na ang wika sa {language_name}",
            "my": f"✅ ဘာသာစကားကို {language_name} အဖြစ်သတ်မှတ်ပြီးပါပြီ",
            "km": f"✅ បានកំណត់ភាសាជា {language_name} ហើយ",
        }
        return confirmations.get(language_code, confirmations["en"])

    def _get_language_list_message(self) -> str:
        return "\n".join(
            [
                "❌ Language not supported | 不支援此語言 | Bahasa tidak didukung | Ngôn ngữ không được hỗ trợ",
                "",
                "✅ Available languages | 可選語言 | Bahasa yang tersedia | Các ngôn ngữ có sẵn:",
                "",
                "🇺🇸 en - English",
                "🇹🇼 zh - Traditional Chinese (繁體中文)",
                "🇮🇩 id - Indonesian (Bahasa Indonesia)",
                "🇻🇳 vi - Vietnamese (Tiếng Việt)",
                "🇹🇭 th - Thai (ภาษาไทย)",
                "🇵🇭 fil - Filipino (Tagalog)",
                "🇲🇲 my - Burmese (မြန်မာဘာသာ)",
                "🇰🇭 km - Khmer (ភាសាខ្មែរ)",
                "",
                "💡 Example: /lang en, /lang zh, /lang id",
            ]
        )

    async def get_user_language_info(self, user_id: str) -> str:
        language_code = await self.db_service.get_user_language(user_id)
        language_name = self.languages.get(language_code, "English")
        return f"Current language: {language_code} ({language_name})"

    async def clear_conversation(self, user_id: str):
        await self.db_service.clear_user_conversation(user_id)
