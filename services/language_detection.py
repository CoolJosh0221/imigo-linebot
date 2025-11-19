"""Language detection service for auto-detecting user input language"""
import logging
from typing import Optional
from langdetect import detect, DetectorFactory, LangDetectException

logger = logging.getLogger(__name__)

# Set seed for consistent results
DetectorFactory.seed = 0


class LanguageDetectionService:
    """Service for detecting the language of user input"""

    # Map langdetect language codes to our supported languages
    LANGUAGE_MAP = {
        "en": "en",  # English
        "zh-cn": "zh",  # Simplified Chinese -> Traditional Chinese
        "zh-tw": "zh",  # Traditional Chinese
        "id": "id",  # Indonesian
        "vi": "vi",  # Vietnamese
        "th": "th",  # Thai
        "tl": "fil",  # Tagalog -> Filipino
    }

    # Supported languages in our system
    SUPPORTED_LANGUAGES = {"en", "zh", "id", "vi", "th", "fil"}

    # Default language if detection fails or language is not supported
    DEFAULT_LANGUAGE = "id"

    def __init__(self, default_language: str = "id"):
        """
        Initialize language detection service

        Args:
            default_language: Default language to use when detection fails
        """
        self.default_language = default_language
        if default_language not in self.SUPPORTED_LANGUAGES:
            logger.warning(
                f"Default language '{default_language}' not supported, using 'id'"
            )
            self.default_language = "id"

    def detect_language(self, text: str) -> str:
        """
        Detect the language of the input text

        Args:
            text: Input text to detect language for

        Returns:
            Language code (en, zh, id, vi, th, fil) or default language if detection fails
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for language detection")
            return self.default_language

        try:
            # Detect language using langdetect
            detected_lang = detect(text.strip())
            logger.info(f"Detected language: {detected_lang} for text: {text[:50]}...")

            # Map to our supported language
            mapped_lang = self.LANGUAGE_MAP.get(detected_lang)

            if mapped_lang and mapped_lang in self.SUPPORTED_LANGUAGES:
                logger.info(f"Mapped to supported language: {mapped_lang}")
                return mapped_lang
            else:
                logger.info(
                    f"Detected language '{detected_lang}' not in supported list, using default: {self.default_language}"
                )
                return self.default_language

        except LangDetectException as e:
            logger.warning(f"Language detection failed: {e}. Using default: {self.default_language}")
            return self.default_language
        except Exception as e:
            logger.error(f"Unexpected error in language detection: {e}. Using default: {self.default_language}")
            return self.default_language

    def get_language_name(self, lang_code: str) -> str:
        """
        Get the full name of a language from its code

        Args:
            lang_code: Language code (en, zh, id, etc.)

        Returns:
            Full language name
        """
        language_names = {
            "en": "English",
            "zh": "Traditional Chinese (繁體中文)",
            "id": "Indonesian (Bahasa Indonesia)",
            "vi": "Vietnamese (Tiếng Việt)",
            "th": "Thai (ภาษาไทย)",
            "fil": "Filipino (Tagalog)",
        }
        return language_names.get(lang_code, "Unknown")

    def is_supported_language(self, lang_code: str) -> bool:
        """
        Check if a language code is supported

        Args:
            lang_code: Language code to check

        Returns:
            True if supported, False otherwise
        """
        return lang_code in self.SUPPORTED_LANGUAGES
