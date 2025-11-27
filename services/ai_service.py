"""AI service for generating responses using LLM"""
import os
import logging
import re
from openai import AsyncOpenAI
from database.database import DatabaseService
from config import BotConfig
from exceptions import AIServiceError, ConfigurationError

logger = logging.getLogger(__name__)

def strip_markdown_formatting(text: str) -> str:
    # Remove bold (**text** and __text__)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"__(.*?)__", r"\1", text)

    # Remove italics (*text* and _text_) – keep content
    text = re.sub(r"(?<!\*)\*(?!\*)(.*?) (?<!\*)\*(?!\*)", r"\1", text)  # safer if space-based, but simple version below is ok for most:
    text = re.sub(r"(?<!\*)\*(.*?)\*(?!\*)", r"\1", text)
    text = re.sub(r"(?<!_)_(.*?)_(?!_)", r"\1", text)

    return text

class AIService:
    def __init__(self, db_service: DatabaseService, config: BotConfig):
        self.db_service = db_service
        self.config = config
        self.client = self._init_client()
        self.model_name = os.getenv("MODEL_NAME", "aisingapore/Llama-SEA-LION-v3.5-8B-R")

        self.languages = {
            "en": "English",
            "zh": "繁體中文",
            "id": "Bahasa Indonesia",
            "vi": "Tiếng Việt",
            "th": "ภาษาไทย",
            "fil": "Tagalog",
        }

    def _init_client(self) -> AsyncOpenAI:
        """Initialize OpenAI client with proper error handling"""
        try:
            base_url = os.getenv("LLM_BASE_URL")
            api_key = os.getenv("LLM_API_KEY", "dummy-key")

            if not base_url:
                if api_key == "dummy-key":
                    raise ConfigurationError("LLM_API_KEY required when using OpenAI")
                return AsyncOpenAI(api_key=api_key)

            return AsyncOpenAI(base_url=base_url, api_key=api_key)
        except Exception as e:
            logger.error(f"Failed to initialize AI client: {e}")
            raise AIServiceError(f"Failed to initialize AI client: {e}") from e

    def _get_system_prompt(self, user_language_code: str = None) -> str:
        """
        Get the system prompt, tailored to the user's language.
        """
        lang_code = user_language_code or self.config.language
        user_language_name = self.languages.get(lang_code, "English")

        return f"""You are {self.config.name}, a kind and helpful AI assistant for migrant workers living in Taiwan.
Your goal is to assist with daily life, labor rights, government services, and language translation.

CURRENT USER SETTINGS:
- User's Language: {user_language_name} ({lang_code})
- Location: Taiwan

CORE INSTRUCTIONS:
1. LANGUAGE:
   - You MUST respond in {user_language_name}.
   - If the user speaks a different language, gently switch to that language and continue.
   - TRANSLATION SPECIFIC: If asked to translate text:
     - The *explanation/label* must be in {user_language_name}.
     - The *translated content* must be in the target language.
     - Example (if user is Indonesian asking for Chinese translation): "Berikut adalah terjemahannya: [Chinese Text]"

2. TONE & STYLE:
   - Be kind, patient, and supportive.
   - Be CONCISE and to the point. Avoid long paragraphs.
   - Use simple, clear language. Avoid complex jargon.
   - Use bullet points (-) for lists.
   - NO Markdown formatting (no bold, italics, etc.). PLAIN TEXT ONLY.

3. KEY INFORMATION (Taiwan Context):
   - Emergency: Police (110), Fire/Ambulance (119).
   - Labor/Foreign Worker Hotline: 1955 (Free, 24/7, multi-lingual).
   - Anti-fraud: 165.
   - Health: Explain NHI (National Health Insurance) simply when asked.

4. SAFETY & RESTRICTIONS:
   - DO NOT provide medical diagnoses or professional legal advice.
   - Always add a disclaimer for health/legal topics: "Please consult a doctor/lawyer for professional advice." or "Information is for reference only." (in {user_language_name}).
   - REMITTANCE: Advise users to only use official, legal channels for sending money home to avoid scams and legal issues.
   - Do not hallucinate. If you don't know, say so and suggest calling 1955.

IMPORTANT:
- Output MUST be PLAIN TEXT only. No **bold** or *italics*.
- If providing an address or phone number, put it on a new line.
"""

    async def aclose(self) -> None:
        # Close underlying HTTP client for AsyncOpenAI
        await self.client.close()

    async def generate_response(self, user_id: str, message: str) -> str:
        """
        Generate AI response for user message

        Args:
            user_id: User ID
            message: User message

        Returns:
            AI generated response

        Raises:
            AIServiceError: If AI generation fails
        """
        try:
            user_language = await self.db_service.get_user_language(user_id)
            # If no language set, default to config but try to detect from message in next steps if needed
            # For now, use config default if None
            if not user_language:
                user_language = self.config.language

            history = await self.db_service.get_conversation_history(
                user_id=user_id, limit=10
            )

            # Pass user_language to get the tailored system prompt
            messages = [{"role": "system", "content": self._get_system_prompt(user_language)}]

            for msg in history:
                messages.append({"role": msg["role"], "content": msg["content"]})

            # We still append the instruction as a reinforcement
            language_name = self.languages.get(user_language, "English")
            messages.append(
                {"role": "user", "content": f"{message}"}
            )

            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
            )

            ai_response = response.choices[0].message.content.strip()
            cleaned_ai_response = re.sub(r"^[\s\S]*?<\/think>\s*", "", ai_response)
            cleaned_ai_response = strip_markdown_formatting(cleaned_ai_response)

            await self.db_service.save_message(user_id, "user", message)
            await self.db_service.save_message(user_id, "assistant", cleaned_ai_response)

            logger.info(f"Response for user {user_id[:8]}... in {user_language}")
            return cleaned_ai_response

        except Exception as e:
            logger.error(f"Failed to generate response for user {user_id[:8]}: {e}")
            raise AIServiceError(f"Failed to generate AI response: {e}") from e

    async def clear_conversation(self, user_id: str):
        await self.db_service.clear_user_conversation(user_id)
