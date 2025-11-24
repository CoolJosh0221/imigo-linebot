import json
import logging
from pathlib import Path
from typing import Optional

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
            with open(image_path, "rb") as f:
                await self.line_api.set_rich_menu_image(
                    rich_menu_id=rich_menu_id,
                    body=f.read(),
                    _headers={"Content-Type": "image/png"},
                )
            logger.info(f"Uploaded image to rich menu: {rich_menu_id}")
            return True
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
