"""Rich Menu management endpoints"""
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/richmenu", tags=["Rich Menu"])


class RichMenuSetupRequest(BaseModel):
    set_as_default: bool = True
    image_path: str = None


class LinkRichMenuRequest(BaseModel):
    user_id: str
    rich_menu_id: str


class UploadImageRequest(BaseModel):
    rich_menu_id: str
    image_path: str


@router.post("/setup")
async def setup_rich_menu(request: RichMenuSetupRequest):
    """
    Create and optionally set as default rich menu

    Args:
        request: Setup configuration

    Returns:
        Created rich menu details
    """
    from main import line_messaging_api
    from services.rich_menu_service import RichMenuService

    try:
        service = RichMenuService(line_messaging_api)

        # Create rich menu
        rich_menu_id = await service.create_rich_menu()
        if not rich_menu_id:
            raise HTTPException(status_code=500, detail="Failed to create rich menu")

        # Upload image if provided
        if request.image_path:
            success = await service.upload_rich_menu_image(rich_menu_id, request.image_path)
            if not success:
                logger.warning(f"Failed to upload image to rich menu {rich_menu_id}")

        # Set as default if requested
        if request.set_as_default:
            success = await service.set_default_rich_menu(rich_menu_id)
            if not success:
                logger.warning(f"Failed to set rich menu {rich_menu_id} as default")

        return {
            "status": "success",
            "rich_menu_id": rich_menu_id,
            "set_as_default": request.set_as_default,
            "image_uploaded": bool(request.image_path),
        }

    except Exception as e:
        logger.error(f"Rich menu setup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-image")
async def upload_rich_menu_image(request: UploadImageRequest):
    """
    Upload an image to an existing rich menu

    Args:
        request: Rich menu ID and image path

    Returns:
        Success status
    """
    from main import line_messaging_api
    from services.rich_menu_service import RichMenuService

    try:
        service = RichMenuService(line_messaging_api)
        success = await service.upload_rich_menu_image(request.rich_menu_id, request.image_path)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to upload image")

        return {
            "status": "success",
            "rich_menu_id": request.rich_menu_id,
        }

    except Exception as e:
        logger.error(f"Upload rich menu image error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_rich_menus():
    """
    Get list of all rich menus

    Returns:
        List of rich menu objects
    """
    from main import line_messaging_api
    from services.rich_menu_service import RichMenuService

    try:
        service = RichMenuService(line_messaging_api)
        menus = await service.get_rich_menu_list()

        return {
            "status": "success",
            "count": len(menus),
            "menus": [
                {
                    "rich_menu_id": menu.rich_menu_id,
                    "name": menu.name,
                    "chat_bar_text": menu.chat_bar_text,
                    "selected": menu.selected,
                }
                for menu in menus
            ],
        }

    except Exception as e:
        logger.error(f"List rich menus error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/default")
async def get_default_rich_menu():
    """
    Get the default rich menu ID

    Returns:
        Default rich menu ID
    """
    from main import line_messaging_api
    from services.rich_menu_service import RichMenuService

    try:
        service = RichMenuService(line_messaging_api)
        rich_menu_id = await service.get_default_rich_menu_id()

        if not rich_menu_id:
            return {"status": "success", "default_rich_menu_id": None}

        return {
            "status": "success",
            "default_rich_menu_id": rich_menu_id,
        }

    except Exception as e:
        logger.error(f"Get default rich menu error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/link")
async def link_rich_menu(request: LinkRichMenuRequest):
    """
    Link a rich menu to a specific user

    Args:
        request: User ID and rich menu ID

    Returns:
        Success status
    """
    from main import line_messaging_api
    from services.rich_menu_service import RichMenuService

    try:
        service = RichMenuService(line_messaging_api)
        success = await service.link_rich_menu_to_user(
            request.user_id, request.rich_menu_id
        )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to link rich menu")

        return {
            "status": "success",
            "user_id": request.user_id,
            "rich_menu_id": request.rich_menu_id,
        }

    except Exception as e:
        logger.error(f"Link rich menu error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/unlink/{user_id}")
async def unlink_rich_menu(user_id: str):
    """
    Unlink rich menu from a user

    Args:
        user_id: LINE user ID

    Returns:
        Success status
    """
    from main import line_messaging_api
    from services.rich_menu_service import RichMenuService

    try:
        service = RichMenuService(line_messaging_api)
        success = await service.unlink_rich_menu_from_user(user_id)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to unlink rich menu")

        return {"status": "success", "user_id": user_id}

    except Exception as e:
        logger.error(f"Unlink rich menu error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{rich_menu_id}")
async def delete_rich_menu(rich_menu_id: str):
    """
    Delete a rich menu

    Args:
        rich_menu_id: Rich menu ID

    Returns:
        Success status
    """
    from main import line_messaging_api
    from services.rich_menu_service import RichMenuService

    try:
        service = RichMenuService(line_messaging_api)
        success = await service.delete_rich_menu(rich_menu_id)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete rich menu")

        return {"status": "success", "rich_menu_id": rich_menu_id}

    except Exception as e:
        logger.error(f"Delete rich menu error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
