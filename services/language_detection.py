"""Language detection service for auto-detecting user input language"""
import logging

from langdetect import DetectorFactory, LangDetectException, detect

logger = logging.getLogger(__name__)

DetectorFactory.seed = 0


class LanguageDetectionService:
    LANGUAGE_MAP = {
        "en": "en",
        "zh-cn": "zh",
        "zh-tw": "zh",
        "id": "id",
        "vi": "vi",
        "th": "th",
        "tl": "fil",
    }

    SUPPORTED_LANGUAGES = {"en", "zh", "id", "vi", "th", "fil"}

    LANGUAGE_NAMES = {
        "en": "English",
        "zh": "Traditional Chinese (繁體中文)",
        "id": "Indonesian (Bahasa Indonesia)",
        "vi": "Vietnamese (Tiếng Việt)",
        "th": "Thai (ภาษาไทย)",
        "fil": "Filipino (Tagalog)",
    }

    def __init__(self, default_language: str = "en"):
        self.default_language = default_language if default_language in self.SUPPORTED_LANGUAGES else "en"
        if default_language != self.default_language:
            logger.warning(f"Default language '{default_language}' not supported, using 'en'")

    def detect_language(self, text: str) -> str:
        if not text or not text.strip():
            logger.warning("Empty text provided for language detection")
            return self.default_language

        try:
            detected_lang = detect(text.strip())
            logger.info(f"Detected language: {detected_lang} for text: {text[:50]}...")

            mapped_lang = self.LANGUAGE_MAP.get(detected_lang)

            if mapped_lang and mapped_lang in self.SUPPORTED_LANGUAGES:
                logger.info(f"Mapped to supported language: {mapped_lang}")
                return mapped_lang

            logger.info(f"Detected language '{detected_lang}' not supported, using default: {self.default_language}")
            return self.default_language

        except (LangDetectException, Exception) as e:
            logger.warning(f"Language detection failed: {e}. Using default: {self.default_language}")
            return self.default_language

    def get_language_name(self, lang_code: str) -> str:
        return self.LANGUAGE_NAMES.get(lang_code, "Unknown")

    def is_supported_language(self, lang_code: str) -> bool:
        return lang_code in self.SUPPORTED_LANGUAGES
