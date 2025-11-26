"""Translation service for group chat messages"""
import logging
import os
from openai import AsyncOpenAI
from config import BotConfig
from exceptions import TranslationError, ConfigurationError

logger = logging.getLogger(__name__)


class TranslationService:
    """LLM-based translation service for group chats"""

    def __init__(self, config: BotConfig):
        self.config = config
        self.client = self._init_client()

        self.language_names = {
            "en": "English",
            "zh": "Traditional Chinese (繁體中文)",
            "id": "Indonesian (Bahasa Indonesia)",
            "vi": "Vietnamese (Tiếng Việt)",
            "th": "Thai (ภาษาไทย)",
            "fil": "Tagalog (Filipino)",
        }

    def _init_client(self) -> AsyncOpenAI:
        """Initialize OpenAI-compatible client for LLM with proper error handling"""
        try:
            base_url = os.getenv("LLM_BASE_URL")
            api_key = os.getenv("LLM_API_KEY", "dummy-key")

            if not base_url:
                if api_key == "dummy-key":
                    raise ConfigurationError("LLM_API_KEY required when using OpenAI")
                return AsyncOpenAI(api_key=api_key)

            return AsyncOpenAI(base_url=base_url, api_key=api_key)
        except Exception as e:
            logger.error(f"Failed to initialize translation client: {e}")
            raise TranslationError(f"Failed to initialize translation client: {e}") from e

    async def translate_message(
        self, text: str, target_language: str, source_language: str = "auto"
    ) -> str:
        """
        Translate message to target language using LLM

        Args:
            text: Text to translate
            target_language: Target language code (id, zh, en, etc.)
            source_language: Source language code or "auto" for auto-detection

        Returns:
            Translated text
        """
        target_lang_name = self.language_names.get(
            target_language, target_language.upper()
        )

        # Create translation prompt
        if source_language == "auto":
            system_prompt = f"""You are a professional translator. Translate the following text to {target_lang_name}.
Only output the translated text, nothing else. Keep the tone and style natural."""
        else:
            source_lang_name = self.language_names.get(
                source_language, source_language.upper()
            )
            system_prompt = f"""You are a professional translator. Translate the following text from {source_lang_name} to {target_lang_name}.
Only output the translated text, nothing else. Keep the tone and style natural."""

        try:
            response = await self.client.chat.completions.create(
                model=self.config.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
                temperature=0.3,  # Lower temperature for more consistent translation
                max_tokens=500,
            )

            translated_text = response.choices[0].message.content.strip()
            logger.info(f"Translated text to {target_language}")
            return translated_text

        except Exception as e:
            logger.error(f"Translation error: {e}")
            raise TranslationError(f"Failed to translate text: {e}") from e

    def format_translation_message(
        self, original_text: str, translated_text: str, target_language: str
    ) -> str:
        """
        Format translation message for group chat

        Args:
            original_text: Original message
            translated_text: Translated message
            target_language: Target language code

        Returns:
            Formatted message with original and translation
        """
        language_flags = {
            "id": "🇮🇩",
            "zh": "🇹🇼",
            "en": "🇬🇧",
            "vi": "🇻🇳",
            "th": "🇹🇭",
            "fil": "🇵🇭",
        }

        flag = language_flags.get(target_language, "🌐")
        lang_name = self.language_names.get(target_language, target_language.upper())

        return f"""{flag} {lang_name}:
{translated_text}"""
