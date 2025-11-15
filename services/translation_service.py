"""Translation service using LLM (MVP)"""

import logging
import os
from typing import Optional
from openai import AsyncOpenAI

log = logging.getLogger(__name__)


class TranslationService:
    """Translation service for personal and group chat (MVP)"""

    # MVP: Only 3 languages
    SUPPORTED_LANGUAGES = {
        "id": "Indonesian (Bahasa Indonesia)",
        "zh": "Traditional Chinese (繁體中文)",
        "en": "English",
    }

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
    ):
        self.base_url = base_url or os.getenv(
            "LLM_BASE_URL", "http://localhost:8000/v1"
        )
        self.api_key = api_key or os.getenv("LLM_API_KEY", "dummy-key")
        self.model_name = model_name or os.getenv(
            "MODEL_NAME", "aisingapore/sea-lion-7b-instruct"
        )
        self.client = AsyncOpenAI(base_url=self.base_url, api_key=self.api_key)

    async def translate(
        self, text: str, source_lang: str, target_lang: str
    ) -> str:
        """
        Translate text from source language to target language.

        Args:
            text: Text to translate
            source_lang: Source language code (id, zh, en)
            target_lang: Target language code (id, zh, en)

        Returns:
            Translated text
        """
        # Validate languages
        if source_lang not in self.SUPPORTED_LANGUAGES:
            log.warning(f"Unsupported source language: {source_lang}")
            return text

        if target_lang not in self.SUPPORTED_LANGUAGES:
            log.warning(f"Unsupported target language: {target_lang}")
            return text

        # Skip if same language
        if source_lang == target_lang:
            return text

        source_lang_name = self.SUPPORTED_LANGUAGES[source_lang]
        target_lang_name = self.SUPPORTED_LANGUAGES[target_lang]

        # Build translation prompt
        system_prompt = (
            f"You are a professional translator specializing in translations "
            f"between Indonesian, Traditional Chinese, and English for migrant workers in Taiwan.\n\n"
            f"Rules:\n"
            f"1. Translate ONLY the text, without adding explanations or comments\n"
            f"2. Preserve the original tone and intent\n"
            f"3. Use natural, conversational language\n"
            f"4. For workplace/labor context, use appropriate formal or informal tone\n"
            f"5. Keep formatting (line breaks, punctuation) when possible\n"
            f"6. Do NOT translate names, brands, or technical terms\n"
            f"7. Output ONLY the translation, nothing else"
        )

        user_prompt = (
            f"Translate the following text from {source_lang_name} to {target_lang_name}:\n\n"
            f"{text}"
        )

        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,  # Lower temperature for consistent translation
                max_tokens=500,
            )

            translation = response.choices[0].message.content.strip()
            log.debug(f"Translated from {source_lang} to {target_lang}")
            return translation

        except Exception as e:
            log.error(f"Translation error: {e}")
            return text  # Return original text on error

    async def auto_detect_and_translate(
        self, text: str, target_lang: str
    ) -> str:
        """
        Auto-detect source language and translate to target language.

        Args:
            text: Text to translate
            target_lang: Target language code (id, zh, en)

        Returns:
            Translated text
        """
        # Simple language detection based on characters
        source_lang = self._detect_language(text)
        return await self.translate(text, source_lang, target_lang)

    def _detect_language(self, text: str) -> str:
        """
        Simple language detection based on character patterns.

        Args:
            text: Text to detect language from

        Returns:
            Detected language code (id, zh, en)
        """
        # Count characters
        chinese_chars = sum(1 for char in text if "\u4e00" <= char <= "\u9fff")
        total_chars = len(text.replace(" ", ""))

        # If >30% Chinese characters, likely Chinese
        if total_chars > 0 and chinese_chars / total_chars > 0.3:
            return "zh"

        # Check for Indonesian common words
        indonesian_words = [
            "yang",
            "dan",
            "di",
            "ke",
            "dari",
            "untuk",
            "dengan",
            "ini",
            "itu",
            "saya",
            "ada",
            "tidak",
            "atau",
        ]
        text_lower = text.lower()
        indonesian_count = sum(
            1 for word in indonesian_words if word in text_lower.split()
        )

        if indonesian_count >= 2:
            return "id"

        # Default to English
        return "en"

    def get_language_name(self, lang_code: str) -> str:
        """Get full language name from code."""
        return self.SUPPORTED_LANGUAGES.get(
            lang_code, self.SUPPORTED_LANGUAGES["id"]
        )
