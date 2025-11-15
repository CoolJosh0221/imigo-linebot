import os
import logging
from openai import AsyncOpenAI
from database.database import DatabaseService
from config import BotConfig

logger = logging.getLogger(__name__)


class AIService:
    """AI service for conversation and assistance (MVP: 3 languages only)"""

    def __init__(self, db_service: DatabaseService, config: BotConfig):
        self.db_service = db_service
        self.config = config
        self.client = self._init_client()
        # MVP: Default to SEA-LION-7B (optimized for Indonesian)
        self.model_name = os.getenv(
            "MODEL_NAME", "aisingapore/sea-lion-7b-instruct"
        )

        # MVP: Only 3 languages
        self.languages = {
            "id": "Bahasa Indonesia",
            "zh": "繁體中文 (Traditional Chinese)",
            "en": "English",
        }

    def _init_client(self) -> AsyncOpenAI:
        base_url = os.getenv("LLM_BASE_URL")
        api_key = os.getenv("LLM_API_KEY", "dummy-key")

        if not base_url:
            if api_key == "dummy-key":
                raise ValueError("LLM_API_KEY required when using OpenAI")
            return AsyncOpenAI(api_key=api_key)

        return AsyncOpenAI(base_url=base_url, api_key=api_key)

    def _get_system_prompt(self) -> str:
        """Generate system prompt for MVP (Translation + Location focus)"""
        bot_identity = f"""You are {self.config.bot.name}, a helpful assistant for Indonesian migrant workers in Taiwan.
Your primary language is {self.languages.get(self.config.bot.language, self.config.bot.language)}."""

        return f"""{bot_identity}

MVP FEATURES
1. Translation assistance (Indonesian ↔ Chinese ↔ English)
2. Location-based help (restaurants, mosques, hospitals, banks, ATMs)
3. General conversation and support

AUDIENCE
Indonesian migrant workers in Taiwan. Most are domestic workers and caregivers.

LANGUAGE
- Respond ONLY in {self.languages.get(self.config.bot.language)}.
- Keep it simple and conversational.
- Use natural, everyday language.

TRANSLATION
- When users send messages for translation, translate naturally.
- Preserve tone and intent.
- Don't add explanations unless asked.

LOCATION HELP
- For location queries, acknowledge and explain that they should use the menu buttons.
- Menu categories: Food (🍽️), Health (🏥), Community (🕌), Emergency (🚨), Services (💰).

FORMAT
- Plain text only. Use hyphens (-) for lists.
- Keep responses concise (2-4 sentences max for simple queries).

EMERGENCY NUMBERS
- Police: 110
- Ambulance/Fire: 119
- Labor Hotline: 1955

STYLE
- Be friendly and supportive.
- Be practical and direct.
- Use ALL CAPS for emphasis, not bold/italic."""

    async def generate_response(self, user_id: str, message: str) -> str:
        user_language = await self.db_service.get_user_language(user_id)
        history = await self.db_service.get_conversation_history(user_id, limit=10)

        messages = [{"role": "system", "content": self._get_system_prompt()}]

        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})

        # MVP: Default to Indonesian if language not found
        language_name = self.languages.get(user_language, "Bahasa Indonesia")
        messages.append(
            {"role": "user", "content": f"[Respond in {language_name}]\n\n{message}"}
        )

        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.7,
            max_tokens=1000,
        )

        ai_response = response.choices[0].message.content.strip()

        await self.db_service.save_message(user_id, "user", message)
        await self.db_service.save_message(user_id, "assistant", ai_response)

        logger.info(f"Response for user {user_id[:8]}... in {user_language}")
        return ai_response

    async def clear_conversation(self, user_id: str):
        await self.db_service.clear_user_conversation(user_id)
