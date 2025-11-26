import json
import logging
from pathlib import Path
from typing import Optional, Dict
import os

from linebot.v3.messaging import (
    AsyncMessagingApi,
    RichMenuRequest,
    RichMenuSize,
    RichMenuArea,
    RichMenuBounds,
    PostbackAction,
)

logger = logging.getLogger(__name__)


class RichMenuService:
    """Service to manage LINE rich menus"""

    def __init__(self, line_api: AsyncMessagingApi):
        self.line_api = line_api
        self.config_path = Path(__file__).parent.parent / "rich_menu" / "menu_config.json"
        self.rich_menu_dir = Path(__file__).parent.parent / "rich_menu"
        # Store rich menu IDs for each language
        self.language_menus: Dict[str, str] = {}  # language_code -> rich_menu_id

    def _validate_image_path(self, image_path: str) -> Path:
        """
        Validate and sanitize image path to prevent path traversal attacks

        Args:
            image_path: Path to validate

        Returns:
            Validated Path object

        Raises:
            ValueError: If path is invalid or outside allowed directory
        """
        # Convert to Path object
        path = Path(image_path).resolve()

        # Ensure the path exists and is a file
        if not path.exists():
            raise ValueError(f"Image file does not exist: {image_path}")

        if not path.is_file():
            raise ValueError(f"Path is not a file: {image_path}")

        # Ensure the path is within the rich_menu directory
        rich_menu_dir_resolved = self.rich_menu_dir.resolve()
        try:
            path.relative_to(rich_menu_dir_resolved)
        except ValueError:
            raise ValueError(f"Image path must be within the rich_menu directory: {image_path}")

        # Validate file extension
        allowed_extensions = {'.png', '.jpg', '.jpeg'}
        if path.suffix.lower() not in allowed_extensions:
            raise ValueError(f"Invalid image format. Allowed: {allowed_extensions}")

        return path

    async def create_rich_menu(self) -> Optional[str]:
        """
        Create a rich menu from the config file

        Returns:
            Rich menu ID if successful, None otherwise
        """
        try:
            # Load config
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            # Create rich menu areas
            areas = []
            for area_config in config.get("areas", []):
                bounds = area_config["bounds"]
                action = area_config["action"]

                # Create action based on type
                if action["type"] == "postback":
                    line_action = PostbackAction(
                        data=action["data"],
                        displayText=action.get("displayText"),
                    )
                else:
                    logger.warning(f"Unsupported action type: {action['type']}")
                    continue

                # Create area
                area = RichMenuArea(
                    bounds=RichMenuBounds(
                        x=bounds["x"],
                        y=bounds["y"],
                        width=bounds["width"],
                        height=bounds["height"],
                    ),
                    action=line_action,
                )
                areas.append(area)

            # Create rich menu request
            size_config = config["size"]
            rich_menu_request = RichMenuRequest(
                size=RichMenuSize(
                    width=size_config["width"],
                    height=size_config["height"],
                ),
                selected=config.get("selected", True),
                name=config.get("name", "IMIGO Menu"),
                chatBarText=config.get("chatBarText", "Tap for Help"),
                areas=areas,
            )

            # Create rich menu
            response = await self.line_api.create_rich_menu(rich_menu_request)
            rich_menu_id = response.rich_menu_id

            logger.info(f"Rich menu created: {rich_menu_id}")
            return rich_menu_id

        except Exception as e:
            logger.error(f"Failed to create rich menu: {e}")
            return None

    async def upload_rich_menu_image(self, rich_menu_id: str, image_path: str) -> bool:
        """
        Upload an image to a rich menu

        Args:
            rich_menu_id: ID of the rich menu
            image_path: Path to the image file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate the image path
            validated_path = self._validate_image_path(image_path)

            # Determine content type from extension
            content_type = "image/png"
            if validated_path.suffix.lower() in {'.jpg', '.jpeg'}:
                content_type = "image/jpeg"

            with open(validated_path, "rb") as f:
                await self.line_api.set_rich_menu_image(
                    rich_menu_id=rich_menu_id,
                    body=f.read(),
                    _headers={"Content-Type": content_type},
                )
            logger.info(f"Uploaded image to rich menu: {rich_menu_id}")
            return True
        except ValueError as e:
            logger.error(f"Invalid image path: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to upload rich menu image: {e}")
            return False

    async def set_default_rich_menu(self, rich_menu_id: str) -> bool:
        """
        Set a rich menu as the default for all users

        Args:
            rich_menu_id: ID of the rich menu

        Returns:
            True if successful, False otherwise
        """
        try:
            await self.line_api.set_default_rich_menu(rich_menu_id)
            logger.info(f"Set default rich menu: {rich_menu_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to set default rich menu: {e}")
            return False

    async def link_rich_menu_to_user(self, user_id: str, rich_menu_id: str) -> bool:
        """
        Link a rich menu to a specific user

        Args:
            user_id: LINE user ID
            rich_menu_id: ID of the rich menu

        Returns:
            True if successful, False otherwise
        """
        try:
            await self.line_api.link_rich_menu_id_to_user(user_id, rich_menu_id)
            logger.info(f"Linked rich menu {rich_menu_id} to user {user_id[:8]}")
            return True
        except Exception as e:
            logger.error(f"Failed to link rich menu to user: {e}")
            return False

    async def unlink_rich_menu_from_user(self, user_id: str) -> bool:
        """
        Unlink a rich menu from a user

        Args:
            user_id: LINE user ID

        Returns:
            True if successful, False otherwise
        """
        try:
            await self.line_api.unlink_rich_menu_id_from_user(user_id)
            logger.info(f"Unlinked rich menu from user {user_id[:8]}")
            return True
        except Exception as e:
            logger.error(f"Failed to unlink rich menu from user: {e}")
            return False

    async def delete_rich_menu(self, rich_menu_id: str) -> bool:
        """
        Delete a rich menu

        Args:
            rich_menu_id: ID of the rich menu

        Returns:
            True if successful, False otherwise
        """
        try:
            await self.line_api.delete_rich_menu(rich_menu_id)
            logger.info(f"Deleted rich menu: {rich_menu_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete rich menu: {e}")
            return False

    async def get_rich_menu_list(self) -> list:
        """
        Get list of all rich menus

        Returns:
            List of rich menu objects
        """
        try:
            response = await self.line_api.get_rich_menu_list()
            return response.richmenus if response else []
        except Exception as e:
            logger.error(f"Failed to get rich menu list: {e}")
            return []

    async def get_default_rich_menu_id(self) -> Optional[str]:
        """
        Get the default rich menu ID

        Returns:
            Rich menu ID if set, None otherwise
        """
        try:
            response = await self.line_api.get_default_rich_menu_id()
            return response.rich_menu_id if response else None
        except Exception as e:
            logger.error(f"Failed to get default rich menu: {e}")
            return None

    async def create_language_rich_menus(self) -> Dict[str, str]:
        """
        Create rich menus for all available languages, or load existing ones

        Returns:
            Dictionary mapping language codes to rich menu IDs
        """
        supported_languages = ["en", "id", "vi", "zh"]
        language_names = {
            "en": "English Menu",
            "id": "Menu Bahasa Indonesia",
            "vi": "Thực đơn Tiếng Việt",
            "zh": "繁體中文選單"
        }

        # Get existing rich menus
        existing_menus = await self.get_rich_menu_list()
        existing_menu_map = {menu.name: menu.rich_menu_id for menu in existing_menus}

        for lang in supported_languages:
            menu_name = language_names.get(lang, f"{lang.upper()} Menu")

            # Check if menu already exists
            if menu_name in existing_menu_map:
                self.language_menus[lang] = existing_menu_map[menu_name]
                logger.info(f"Reusing existing rich menu for language {lang}: {existing_menu_map[menu_name]}")
                continue

            # Create new menu if it doesn't exist
            image_path = self.rich_menu_dir / f"menu_{lang}.png"

            if not image_path.exists():
                logger.warning(f"Image not found for language {lang}: {image_path}")
                continue

            try:
                # Create rich menu
                rich_menu_id = await self.create_rich_menu_for_language(lang, menu_name)

                if rich_menu_id:
                    # Upload image
                    success = await self.upload_rich_menu_image(rich_menu_id, str(image_path))

                    if success:
                        self.language_menus[lang] = rich_menu_id
                        logger.info(f"Created new rich menu for language {lang}: {rich_menu_id}")
                    else:
                        logger.error(f"Failed to upload image for language {lang}")
                        await self.delete_rich_menu(rich_menu_id)

            except Exception as e:
                logger.error(f"Failed to create rich menu for language {lang}: {e}")

        return self.language_menus

    async def create_rich_menu_for_language(self, language: str, menu_name: str) -> Optional[str]:
        """
        Create a rich menu for a specific language

        Args:
            language: Language code (en, id, vi, zh)
            menu_name: Name for the rich menu

        Returns:
            Rich menu ID if successful, None otherwise
        """
        try:
            # Load config
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            # Create rich menu areas
            areas = []
            for area_config in config.get("areas", []):
                bounds = area_config["bounds"]
                action = area_config["action"]

                # Create action based on type
                if action["type"] == "postback":
                    line_action = PostbackAction(
                        data=action["data"],
                        displayText=action.get("displayText"),
                    )
                else:
                    logger.warning(f"Unsupported action type: {action['type']}")
                    continue

                # Create area
                area = RichMenuArea(
                    bounds=RichMenuBounds(
                        x=bounds["x"],
                        y=bounds["y"],
                        width=bounds["width"],
                        height=bounds["height"],
                    ),
                    action=line_action,
                )
                areas.append(area)

            # Create rich menu request with language-specific name
            size_config = config["size"]
            rich_menu_request = RichMenuRequest(
                size=RichMenuSize(
                    width=size_config["width"],
                    height=size_config["height"],
                ),
                selected=config.get("selected", True),
                name=menu_name,
                chatBarText=config.get("chatBarText", "Tap for Help 點擊求助"),
                areas=areas,
            )

            # Create rich menu
            response = await self.line_api.create_rich_menu(rich_menu_request)
            rich_menu_id = response.rich_menu_id

            logger.info(f"Rich menu created for {language}: {rich_menu_id}")
            return rich_menu_id

        except Exception as e:
            logger.error(f"Failed to create rich menu for language {language}: {e}")
            return None

    def get_rich_menu_for_language(self, language: str) -> Optional[str]:
        """
        Get the rich menu ID for a specific language

        Args:
            language: Language code (en, id, vi, zh)

        Returns:
            Rich menu ID if available, None otherwise
        """
        return self.language_menus.get(language)

    async def set_user_rich_menu(self, user_id: str, language: str) -> bool:
        """
        Set the appropriate rich menu for a user based on their language preference

        Args:
            user_id: LINE user ID
            language: User's preferred language code

        Returns:
            True if successful, False otherwise
        """
        rich_menu_id = self.get_rich_menu_for_language(language)

        if not rich_menu_id:
            logger.warning(f"No rich menu found for language {language}")
            return False

        return await self.link_rich_menu_to_user(user_id, rich_menu_id)

    async def cleanup_all_rich_menus(self) -> bool:
        """
        Delete all rich menus (useful for cleanup/reset)

        Returns:
            True if all deletions successful, False otherwise
        """
        try:
            menus = await self.get_rich_menu_list()

            for menu in menus:
                await self.delete_rich_menu(menu.rich_menu_id)
                logger.info(f"Deleted rich menu: {menu.rich_menu_id}")

            self.language_menus.clear()
            return True

        except Exception as e:
            logger.error(f"Failed to cleanup rich menus: {e}")
            return False
