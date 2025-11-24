import re
import logging
from typing import Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class Intent(str, Enum):
    """User intent types"""
    COMMAND = "command"
    GREETING = "greeting"
    THANKS = "thanks"
    GOODBYE = "goodbye"
    EMERGENCY = "emergency"
    HELP = "help"
    QUERY = "query"


class IntentService:
    """Service to detect user intent from messages"""

    def __init__(self):
        # Patterns for different intents (multi-language)
        self.patterns = {
            Intent.COMMAND: [
                r"^/\w+",  # Slash commands
            ],
            Intent.GREETING: [
                r"\b(hi|hello|hey|halo|hai|hola|你好|您好|早安|午安|晚安|selamat pagi|selamat siang|selamat malam)\b",
            ],
            Intent.THANKS: [
                r"\b(thanks?|thank you|thx|terima kasih|makasih|谢谢|謝謝)\b",
            ],
            Intent.GOODBYE: [
                r"\b(bye|goodbye|see you|sampai jumpa|再見|拜拜)\b",
            ],
            Intent.EMERGENCY: [
                r"\b(emergency|urgent|darurat|緊急|紧急|help me|tolong|救命)\b",
                r"\b(injured|hurt|accident|kecelakaan|受傷|受伤)\b",
            ],
            Intent.HELP: [
                r"\b(help|bantuan|幫助|帮助|how to|cara)\b",
            ],
        }

        # Quick responses for simple intents
        self.quick_responses = {
            Intent.GREETING: {
                "id": "Halo! 👋 Saya IMIGO, asisten untuk pekerja migran di Taiwan. Ada yang bisa saya bantu?",
                "zh": "您好！👋 我是 IMIGO，台灣移工的助手。有什麼可以幫您的嗎？",
                "en": "Hello! 👋 I'm IMIGO, assistant for migrant workers in Taiwan. How can I help you?",
            },
            Intent.THANKS: {
                "id": "Sama-sama! 😊 Senang bisa membantu. Ada lagi yang perlu ditanyakan?",
                "zh": "不客氣！😊 很高興能幫到您。還有其他問題嗎？",
                "en": "You're welcome! 😊 Happy to help. Anything else you need?",
            },
            Intent.GOODBYE: {
                "id": "Sampai jumpa! 👋 Jangan ragu untuk menghubungi saya kapan saja.",
                "zh": "再見！👋 隨時歡迎您再來。",
                "en": "Goodbye! 👋 Feel free to reach out anytime.",
            },
        }

    def detect_intent(self, text: str) -> Intent:
        """
        Detect user intent from message text

        Args:
            text: User message

        Returns:
            Detected intent
        """
        text_lower = text.lower().strip()

        # Check patterns in order of priority
        for intent, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    logger.info(f"Detected intent: {intent} from text: {text[:50]}")
                    return intent

        # Default to query if no specific intent detected
        return Intent.QUERY

    def get_quick_response(self, intent: Intent, language: str) -> Optional[str]:
        """
        Get a quick response for simple intents

        Args:
            intent: Detected intent
            language: User's language code

        Returns:
            Quick response text if available, None otherwise
        """
        if intent not in self.quick_responses:
            return None

        responses = self.quick_responses[intent]
        return responses.get(language, responses.get("en"))

    def should_use_ai(self, intent: Intent) -> bool:
        """
        Determine if AI should handle this intent

        Args:
            intent: Detected intent

        Returns:
            True if AI should handle, False for quick response
        """
        # Use quick responses for simple intents
        simple_intents = {Intent.GREETING, Intent.THANKS, Intent.GOODBYE}
        return intent not in simple_intents

    def extract_command(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract command and arguments from text

        Args:
            text: User message

        Returns:
            Tuple of (command, args) or (None, None)
        """
        match = re.match(r"^/(\w+)\s*(.*)", text.strip(), re.IGNORECASE)
        if match:
            command = match.group(1).lower()
            args = match.group(2).strip() or None
            return command, args
        return None, None

    def is_emergency(self, text: str) -> bool:
        """
        Check if message indicates an emergency

        Args:
            text: User message

        Returns:
            True if emergency detected
        """
        return self.detect_intent(text) == Intent.EMERGENCY
