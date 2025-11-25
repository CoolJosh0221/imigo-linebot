"""
Service Container for dependency management and initialization
"""
import logging
from typing import Optional

from linebot.v3.messaging import AsyncMessagingApi, AsyncApiClient, Configuration
from linebot.v3.webhook import WebhookParser

from config import Config
from database.database import DatabaseService
from services.ai_service import AIService
from services.translation_service import TranslationService
from services.language_detection import LanguageDetectionService
from services.rich_menu_service import RichMenuService

logger = logging.getLogger(__name__)


class ServiceContainer:
    """Container for managing service instances and their lifecycle"""

    def __init__(self):
        self.db_service: Optional[DatabaseService] = None
        self.ai_service: Optional[AIService] = None
        self.translation_service: Optional[TranslationService] = None
        self.language_detection_service: Optional[LanguageDetectionService] = None
        self.rich_menu_service: Optional[RichMenuService] = None
        self.line_messaging_api: Optional[AsyncMessagingApi] = None
        self.line_parser: Optional[WebhookParser] = None
        self._line_async_client: Optional[AsyncApiClient] = None
        self._initialized = False

    async def initialize(self, config: Config):
        """
        Initialize all services with the given configuration

        Args:
            config: Application configuration
        """
        if self._initialized:
            logger.warning("Services already initialized")
            return

        logger.info("Initializing services...")

        # Initialize database
        self.db_service = DatabaseService()
        await self.db_service.init_db()
        logger.info("Database service initialized")

        # Initialize AI and translation services
        self.ai_service = AIService(self.db_service, config)
        self.translation_service = TranslationService(config)
        self.language_detection_service = LanguageDetectionService(
            default_language=config.language
        )
        logger.info("AI and translation services initialized")

        # Initialize LINE API
        line_config = Configuration(access_token=config.line_token)
        self._line_async_client = AsyncApiClient(line_config)
        self.line_messaging_api = AsyncMessagingApi(self._line_async_client)
        self.line_parser = WebhookParser(config.line_secret)
        logger.info("LINE API services initialized")

        # Initialize rich menu service
        self.rich_menu_service = RichMenuService(self.line_messaging_api)
        logger.info("Rich menu service initialized")

        # Set up language-specific rich menus
        await self._setup_rich_menus()

        self._initialized = True
        logger.info("All services initialized successfully")

    async def _setup_rich_menus(self):
        """Set up language-specific rich menus"""
        try:
            logger.info("Setting up language-specific rich menus...")
            language_menus = await self.rich_menu_service.create_language_rich_menus()

            if language_menus:
                logger.info(
                    f"Rich menus ready for {len(language_menus)} languages: "
                    f"{list(language_menus.keys())}"
                )
            else:
                logger.warning("No rich menus were created")
        except Exception as e:
            logger.error(f"Failed to set up rich menus: {e}", exc_info=True)

    async def cleanup(self):
        """Clean up resources"""
        if self._line_async_client:
            await self._line_async_client.close()
            logger.info("LINE API client closed")

        self._initialized = False
        logger.info("Services cleaned up")

    def is_initialized(self) -> bool:
        """Check if services are initialized"""
        return self._initialized


# Global service container instance
_container: Optional[ServiceContainer] = None


def get_container() -> ServiceContainer:
    """Get the global service container instance"""
    global _container
    if _container is None:
        _container = ServiceContainer()
    return _container


async def initialize_services(config: Config) -> ServiceContainer:
    """
    Initialize all services with the given configuration

    Args:
        config: Application configuration

    Returns:
        Initialized service container
    """
    container = get_container()
    await container.initialize(config)
    return container


async def cleanup_services():
    """Clean up all services"""
    container = get_container()
    await container.cleanup()
