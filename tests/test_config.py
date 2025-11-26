"""Tests for configuration module"""
import pytest
import os
from config import BotConfig, SUPPORTED_LANGUAGES, MESSAGES, load_config, get_config
from exceptions import ConfigurationError


class TestBotConfig:
    """Test BotConfig class"""

    def test_config_initialization_success(self, test_env):
        """Test successful configuration initialization"""
        config = BotConfig()
        assert config.name == "IMIGO"
        assert config.country == "tw"
        assert config.language == "id"
        assert config.line_secret == "test-secret"
        assert config.line_token == "test-token"

    def test_config_missing_line_credentials(self):
        """Test that missing LINE credentials raises error"""
        os.environ.pop("LINE_CHANNEL_SECRET", None)
        os.environ.pop("LINE_CHANNEL_ACCESS_TOKEN", None)

        with pytest.raises(ConfigurationError, match="LINE_CHANNEL_SECRET"):
            BotConfig()

    def test_config_invalid_language(self, test_env):
        """Test that invalid default language raises error"""
        os.environ["DEFAULT_LANGUAGE"] = "invalid"

        with pytest.raises(ConfigurationError, match="Invalid DEFAULT_LANGUAGE"):
            BotConfig()

    def test_config_cors_origins_parsing(self, test_env):
        """Test CORS origins parsing"""
        os.environ["CORS_ORIGINS"] = "http://localhost:3000,https://example.com"
        config = BotConfig()
        assert len(config.cors_origins) == 2
        assert "http://localhost:3000" in config.cors_origins
        assert "https://example.com" in config.cors_origins

    def test_config_cors_origins_default(self, test_env):
        """Test default CORS origins"""
        os.environ.pop("CORS_ORIGINS", None)
        config = BotConfig()
        assert "http://localhost:3000" in config.cors_origins
        assert "http://localhost:8000" in config.cors_origins

    def test_config_invalid_cors_origin(self, test_env):
        """Test that invalid CORS origin raises error"""
        os.environ["CORS_ORIGINS"] = "invalid-url"

        with pytest.raises(ConfigurationError, match="Invalid CORS origin"):
            BotConfig()

        # Cleanup
        os.environ.pop("CORS_ORIGINS", None)

    def test_get_message(self, test_env):
        """Test getting localized messages"""
        os.environ.pop("CORS_ORIGINS", None)  # Ensure clean state
        config = BotConfig()

        # Test with default language
        msg = config.get_message("welcome")
        assert "IMIGO" in msg

        # Test with specified language
        msg_en = config.get_message("welcome", "en")
        assert "Welcome" in msg_en

        msg_zh = config.get_message("welcome", "zh")
        assert "歡迎" in msg_zh

    def test_get_emergency_info(self, test_env):
        """Test emergency contact information"""
        config = BotConfig()
        info = config.get_emergency_info()

        assert "110" in info  # Police
        assert "119" in info  # Ambulance
        assert "1955" in info  # Labor hotline

    def test_is_valid_language(self, test_env):
        """Test language validation"""
        config = BotConfig()

        assert config.is_valid_language("id") is True
        assert config.is_valid_language("en") is True
        assert config.is_valid_language("zh") is True
        assert config.is_valid_language("vi") is True
        assert config.is_valid_language("invalid") is False


class TestConfigManagement:
    """Test config management functions"""

    def test_load_and_get_config(self, test_env):
        """Test loading and retrieving config"""
        config = load_config()
        assert config is not None

        retrieved_config = get_config()
        assert retrieved_config is config

    def test_get_config_before_load(self):
        """Test that getting config before loading raises error"""
        # Reset the global config
        import config as config_module

        config_module._config = None

        with pytest.raises(RuntimeError, match="Config not loaded"):
            get_config()


class TestSupportedLanguages:
    """Test supported languages configuration"""

    def test_supported_languages_defined(self):
        """Test that all supported languages are defined"""
        assert "id" in SUPPORTED_LANGUAGES
        assert "zh" in SUPPORTED_LANGUAGES
        assert "en" in SUPPORTED_LANGUAGES
        assert "vi" in SUPPORTED_LANGUAGES

    def test_messages_for_all_languages(self):
        """Test that messages exist for all supported languages"""
        for lang in SUPPORTED_LANGUAGES.keys():
            assert lang in MESSAGES
            assert "welcome" in MESSAGES[lang]
            assert "help" in MESSAGES[lang]
            assert "cleared" in MESSAGES[lang]
