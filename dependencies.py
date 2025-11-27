"""
Dependency injection for FastAPI endpoints and webhook handlers.

This module provides clean dependency injection without a container pattern.
Services are lazily initialized and cached for the application lifetime.
"""
import logging
from typing import Optional
from functools import lru_cache

from linebot.v3.messaging import AsyncMessagingApi, AsyncMessagingApiBlob, AsyncApiClient, Configuration
from linebot.v3.webhook import WebhookParser

from config import BotConfig, get_config
from database.database import DatabaseService
from services.ai_service import AIService
from services.translation_service import TranslationService
from services.language_detection import LanguageDetectionService
from services.rich_menu_service import RichMenuService

logger = logging.getLogger(__name__)

# Global service instances (initialized on first use)
_db_service: Optional[DatabaseService] = None
_ai_service: Optional[AIService] = None
_translation_service: Optional[TranslationService] = None
_language_detection_service: Optional[LanguageDetectionService] = None
_rich_menu_service: Optional[RichMenuService] = None
_line_messaging_api: Optional[AsyncMessagingApi] = None
_line_messaging_api_blob: Optional[AsyncMessagingApiBlob] = None
_line_parser: Optional[WebhookParser] = None
_line_async_client: Optional[AsyncApiClient] = None


async def get_database_service() -> DatabaseService:
    """Get or create database service instance"""
    global _db_service
    if _db_service is None:
        config = get_config()
        _db_service = DatabaseService(db_url=config.db_url)
        await _db_service.init_db()
        logger.info("Database service initialized")
    return _db_service


async def get_ai_service() -> AIService:
    """Get or create AI service instance"""
    global _ai_service
    if _ai_service is None:
        config = get_config()
        db_service = await get_database_service()
        _ai_service = AIService(db_service, config)
        logger.info("AI service initialized")
    return _ai_service


async def get_translation_service() -> TranslationService:
    """Get or create translation service instance"""
    global _translation_service
    if _translation_service is None:
        config = get_config()
        _translation_service = TranslationService(config)
        logger.info("Translation service initialized")
    return _translation_service


async def get_language_detection_service() -> LanguageDetectionService:
    """Get or create language detection service instance"""
    global _language_detection_service
    if _language_detection_service is None:
        config = get_config()
        _language_detection_service = LanguageDetectionService(
            default_language=config.language
        )
        logger.info("Language detection service initialized")
    return _language_detection_service


async def get_line_messaging_api() -> AsyncMessagingApi:
    """Get or create LINE messaging API instance"""
    global _line_messaging_api, _line_messaging_api_blob, _line_async_client
    if _line_messaging_api is None:
        config = get_config()
        line_config = Configuration(access_token=config.line_token)
        _line_async_client = AsyncApiClient(line_config)
        _line_messaging_api = AsyncMessagingApi(_line_async_client)
        _line_messaging_api_blob = AsyncMessagingApiBlob(_line_async_client)
        logger.info("LINE messaging API initialized")
    return _line_messaging_api


async def get_line_messaging_api_blob() -> AsyncMessagingApiBlob:
    """Get or create LINE messaging API blob instance"""
    global _line_messaging_api_blob
    if _line_messaging_api_blob is None:
        # Initialize messaging API first (which also initializes blob API)
        await get_line_messaging_api()
    return _line_messaging_api_blob


async def get_rich_menu_service() -> RichMenuService:
    """Get or create rich menu service instance"""
    global _rich_menu_service
    if _rich_menu_service is None:
        line_api = await get_line_messaging_api()
        blob_api = await get_line_messaging_api_blob()
        _rich_menu_service = RichMenuService(line_api, blob_api)
        logger.info("Rich menu service initialized")
    return _rich_menu_service


def get_line_parser() -> WebhookParser:
    """Get or create LINE webhook parser instance"""
    global _line_parser
    if _line_parser is None:
        config = get_config()
        _line_parser = WebhookParser(config.line_secret)
        logger.info("LINE webhook parser initialized")
    return _line_parser


async def initialize_services():
    """Initialize all services on application startup"""
    logger.info("Initializing all services...")

    # Initialize services in order
    await get_database_service()
    await get_ai_service()
    await get_translation_service()
    await get_language_detection_service()
    await get_line_messaging_api()
    rich_menu_service = await get_rich_menu_service()
    get_line_parser()

    # Set up language-specific rich menus
    try:
        logger.info("Setting up language-specific rich menus...")
        language_menus = await rich_menu_service.create_language_rich_menus()

        if language_menus:
            logger.info(
                f"Rich menus ready for {len(language_menus)} languages: "
                f"{list(language_menus.keys())}"
            )
        else:
            logger.warning("No rich menus were created")
    except Exception as e:
        logger.error(f"Failed to set up rich menus: {e}", exc_info=True)

    logger.info("All services initialized successfully")


async def cleanup_services():
    """Clean up all services on application shutdown"""
    global _ai_service, _translation_service, _db_service, _line_async_client
    global _rich_menu_service, _language_detection_service, _line_messaging_api, _line_messaging_api_blob, _line_parser

    logger.info("Cleaning up services...")

    # Close AI service
    if _ai_service:
        try:
            await _ai_service.aclose()
        except Exception as e:
            logger.error(f"Error closing AI service: {e}")

    # Close translation service
    if _translation_service:
        try:
            await _translation_service.aclose()
        except Exception as e:
            logger.error(f"Error closing translation service: {e}")

    # Close database
    if _db_service:
        try:
            await _db_service.dispose()
            logger.info("Database service disposed")
        except Exception as e:
            logger.error(f"Error disposing database: {e}")

    # Close LINE API client
    if _line_async_client:
        try:
            await _line_async_client.close()
            logger.info("LINE API client closed")
        except Exception as e:
            logger.error(f"Error closing LINE API client: {e}")

    # Reset all globals
    _db_service = None
    _ai_service = None
    _translation_service = None
    _language_detection_service = None
    _rich_menu_service = None
    _line_messaging_api = None
    _line_messaging_api_blob = None
    _line_parser = None
    _line_async_client = None

    logger.info("All services cleaned up successfully")
