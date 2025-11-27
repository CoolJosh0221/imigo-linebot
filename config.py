"""Configuration management for IMIGO LINE Bot"""
import os
from typing import Dict, Optional, List
from dotenv import load_dotenv
from exceptions import ConfigurationError


# Language-specific messages
MESSAGES = {
    "id": {
        "welcome": """👋 Selamat datang di IMIGO!

Saya adalah asisten AI untuk membantu pekerja migran Indonesia di Taiwan.

Saya dapat membantu dengan:
• Informasi ketenagakerjaan
• Layanan pemerintah
• Terjemahan bahasa
• Informasi kesehatan
• Kehidupan sehari-hari

Silakan ajukan pertanyaan Anda!""",
        "cleared": "✅ Riwayat percakapan telah dihapus.\nAnda dapat memulai percakapan baru!",
        "language_changed": "✅ Bahasa telah diubah ke Bahasa Indonesia.\nSaya sekarang akan merespons dalam bahasa Indonesia!",
        "language_select": "🌐 Pilih bahasa Anda:\nKetik: /lang id (Indonesia)\n/lang zh (中文)\n/lang en (English)",
        "help": """🤖 Cara menggunakan IMIGO:

Ketik pertanyaan Anda dalam bahasa apa pun, dan saya akan membantu!

Kategori bantuan:
• 💼 Masalah pekerjaan
• 🏛️ Layanan pemerintah
• 🏥 Informasi kesehatan
• 🌐 Bantuan terjemahan
• 🏠 Kehidupan sehari-hari
• 🚨 Kontak darurat""",
    },
    "zh": {
        "welcome": """👋 歡迎使用 IMIGO！

我是協助在台灣的印尼移工的 AI 助手。

我可以幫助您：
• 勞工資訊
• 政府服務
• 語言翻譯
• 健康資訊
• 日常生活

請隨時提出您的問題！""",
        "cleared": "✅ 對話記錄已清除。\n您可以開始新的對話！",
        "language_changed": "✅ 語言已更改為繁體中文。\n我現在將用中文回應！",
        "language_select": "🌐 選擇您的語言：\n輸入: /lang id (印尼文)\n/lang zh (中文)\n/lang en (英文)",
        "help": """🤖 如何使用 IMIGO：

用任何語言輸入您的問題，我會幫助您！

協助類別：
• 💼 工作問題
• 🏛️ 政府服務
• 🏥 健康資訊
• 🌐 翻譯協助
• 🏠 日常生活
• 🚨 緊急聯絡""",
    },
    "en": {
        "welcome": """👋 Welcome to IMIGO!

I'm an AI assistant to help Indonesian migrant workers in Taiwan.

I can help with:
• Labor information
• Government services
• Language translation
• Health information
• Daily life

Please ask me anything!""",
        "cleared": "✅ Chat history has been cleared.\nYou can start a new conversation!",
        "language_changed": "✅ Language changed to English.\nI will now respond in English!",
        "language_select": "🌐 Choose your language:\nType: /lang id (Indonesian)\n/lang zh (Chinese)\n/lang en (English)\n/lang vi (Vietnamese)",
        "help": """🤖 How to use IMIGO:

Type your question in any language, and I'll help you!

Help categories:
• 💼 Work problems
• 🏛️ Government services
• 🏥 Health information
• 🌐 Translation help
• 🏠 Daily life
• 🚨 Emergency contacts""",
    },
    "vi": {
        "welcome": """👋 Chào mừng đến với IMIGO!

Tôi là trợ lý AI giúp đỡ lao động nhập cư tại Đài Loan.

Tôi có thể giúp với:
• Thông tin lao động
• Dịch vụ chính phủ
• Dịch thuật ngôn ngữ
• Thông tin y tế
• Cuộc sống hàng ngày

Hãy hỏi tôi bất cứ điều gì!""",
        "cleared": "✅ Lịch sử trò chuyện đã được xóa.\nBạn có thể bắt đầu cuộc trò chuyện mới!",
        "language_changed": "✅ Đã đổi sang Tiếng Việt.\nTôi sẽ trả lời bằng Tiếng Việt!",
        "language_select": "🌐 Chọn ngôn ngữ của bạn:\nNhập: /lang id (Tiếng Indonesia)\n/lang zh (Tiếng Trung)\n/lang en (Tiếng Anh)\n/lang vi (Tiếng Việt)",
        "help": """🤖 Cách sử dụng IMIGO:

Nhập câu hỏi của bạn bằng bất kỳ ngôn ngữ nào, tôi sẽ giúp bạn!

Các loại hỗ trợ:
• 💼 Vấn đề công việc
• 🏛️ Dịch vụ chính phủ
• 🏥 Thông tin y tế
• 🌐 Hỗ trợ dịch thuật
• 🏠 Cuộc sống hàng ngày
• 🚨 Liên hệ khẩn cấp""",
    },
}

# Supported languages
SUPPORTED_LANGUAGES = {
    "id": "Bahasa Indonesia",
    "zh": "繁體中文",
    "en": "English",
    "vi": "Tiếng Việt",
}

# Language-specific chat bar text for rich menus (max 14 characters)
CHAT_BAR_TEXT = {
    "id": "Bantuan",  # Help in Indonesian
    "zh": "幫助",  # Help in Chinese
    "en": "Help",  # Help in English
    "vi": "Trợ giúp",  # Help in Vietnamese
}

# Emergency contacts for Taiwan
EMERGENCY_CONTACTS = {
    "police": "110",
    "fire_ambulance": "119",
    "foreign_worker_hotline": "1955",
    "indonesia_representative": "+886-2-2356-5156",
    "labor_hotline": "1955",
    "anti_trafficking_hotline": "113",
}


class BotConfig:
    """Configuration class for IMIGO LINE Bot"""

    def __init__(self):
        load_dotenv()

        # Bot identity
        self.language = self._get_env_with_default("DEFAULT_LANGUAGE", "en")
        self.name = "IMIGO"
        self.country = "tw"

        # Validate language
        if not self.is_valid_language(self.language):
            raise ConfigurationError(
                f"Invalid DEFAULT_LANGUAGE: {self.language}. "
                f"Must be one of: {', '.join(SUPPORTED_LANGUAGES.keys())}"
            )

        # LINE credentials
        self.line_secret = os.getenv("LINE_CHANNEL_SECRET")
        self.line_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

        # LLM configuration
        self.llm_base_url = self._get_env_with_default(
            "LLM_BASE_URL", "http://localhost:8000/v1"
        )
        self.model_name = self._get_env_with_default(
            "MODEL_NAME", "aisingapore/sealion7b-instruct"
        )

        # Database
        self.db_url = self._get_env_with_default(
            "DATABASE_URL", "sqlite+aiosqlite:///database.db"
        )

        # CORS settings
        self.cors_origins = self._parse_cors_origins()

        # Validate required fields
        self._validate_config()

    def _get_env_with_default(self, key: str, default: str) -> str:
        """Get environment variable with default value"""
        return os.getenv(key, default).strip()

    def _parse_cors_origins(self) -> List[str]:
        """Parse CORS origins from environment"""
        cors_origins = os.getenv("CORS_ORIGINS", "")
        if cors_origins:
            origins = [origin.strip() for origin in cors_origins.split(",")]
            # Validate origins
            for origin in origins:
                if origin and not self._is_valid_origin(origin):
                    raise ConfigurationError(
                        f"Invalid CORS origin: {origin}. "
                        "Must be a valid URL or '*' for all origins."
                    )
            return origins
        # Default to localhost only for development
        return ["http://localhost:3000", "http://localhost:8000"]

    def _is_valid_origin(self, origin: str) -> bool:
        """Validate CORS origin format"""
        if origin == "*":
            return True
        # Basic URL validation
        return origin.startswith("http://") or origin.startswith("https://")

    def _validate_config(self):
        """Validate required configuration"""
        if not self.line_secret or not self.line_token:
            raise ConfigurationError(
                "LINE_CHANNEL_SECRET and LINE_CHANNEL_ACCESS_TOKEN "
                "must be set in environment variables"
            )

        if not self.llm_base_url:
            raise ConfigurationError("LLM_BASE_URL must be set")

        if not self.model_name:
            raise ConfigurationError("MODEL_NAME must be set")

    def get_message(self, key: str, language: str = None) -> str:
        """Get a message in the specified language (or bot's default language)"""
        lang = language or self.language
        lang_messages = MESSAGES.get(lang, MESSAGES["en"])
        return lang_messages.get(key, key)

    def get_emergency_info(self) -> str:
        """Get formatted emergency contact information"""
        lines = ["🚨 EMERGENCY CONTACTS:"]
        for label, value in EMERGENCY_CONTACTS.items():
            lines.append(f"- {label.replace('_', ' ').title()}: {value}")
        return "\n".join(lines)

    @staticmethod
    def is_valid_language(lang_code: str) -> bool:
        """Check if a language code is supported"""
        return lang_code in SUPPORTED_LANGUAGES

    @staticmethod
    def get_chat_bar_text(lang_code: str) -> str:
        """Get chat bar text for rich menu in specified language"""
        return CHAT_BAR_TEXT.get(lang_code, "Help")


_config: Optional[BotConfig] = None


def load_config() -> BotConfig:
    """Load configuration from environment variables"""
    global _config
    _config = BotConfig()
    return _config


def get_config() -> BotConfig:
    """Get the loaded configuration"""
    if _config is None:
        raise RuntimeError("Config not loaded. Call load_config() first.")
    return _config
