"""Rich Menu management endpoints"""
import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from services.rich_menu_service import RichMenuService
from services.container import get_container

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


def get_rich_menu_svc() -> RichMenuService:
    """Get rich menu service from service container"""
    return get_container().rich_menu_service


@router.post("/setup")
async def setup_rich_menu(
    request: RichMenuSetupRequest,
    service: RichMenuService = Depends(get_rich_menu_svc)
):
    """
    Create and optionally set as default rich menu (legacy single-menu setup)

    Args:
        request: Setup configuration

    Returns:
        Created rich menu details
    """
    try:
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


@router.post("/setup-language-menus")
async def setup_language_menus(
    service: RichMenuService = Depends(get_rich_menu_svc)
):
    """
    Create or load language-specific rich menus for all supported languages

    This endpoint sets up rich menus for English, Indonesian, Vietnamese, and Chinese.
    It automatically reuses existing menus if they already exist.

    Returns:
        Dictionary with created/loaded menu IDs for each language
    """
    try:
        logger.info("Setting up language-specific rich menus...")
        language_menus = await service.create_language_rich_menus()

        if not language_menus:
            raise HTTPException(
                status_code=500,
                detail="No rich menus were created. Check if menu images exist in rich_menu/ directory."
            )

        return {
            "status": "success",
            "language_count": len(language_menus),
            "languages": list(language_menus.keys()),
            "menus": {
                lang: {"rich_menu_id": menu_id}
                for lang, menu_id in language_menus.items()
            },
        }

    except Exception as e:
        logger.error(f"Language menu setup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-image")
async def upload_rich_menu_image(
    request: UploadImageRequest,
    service: RichMenuService = Depends(get_rich_menu_svc)
):
    """
    Upload an image to an existing rich menu

    Args:
        request: Rich menu ID and image path

    Returns:
        Success status
    """
    try:
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
async def list_rich_menus(service: RichMenuService = Depends(get_rich_menu_svc)):
    """
    Get list of all rich menus

    Returns:
        List of rich menu objects
    """
    try:
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
async def get_default_rich_menu(service: RichMenuService = Depends(get_rich_menu_svc)):
    """
    Get the default rich menu ID

    Returns:
        Default rich menu ID
    """
    try:
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
async def link_rich_menu(
    request: LinkRichMenuRequest,
    service: RichMenuService = Depends(get_rich_menu_svc)
):
    """
    Link a rich menu to a specific user

    Args:
        request: User ID and rich menu ID

    Returns:
        Success status
    """
    try:
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
async def unlink_rich_menu(
    user_id: str,
    service: RichMenuService = Depends(get_rich_menu_svc)
):
    """
    Unlink rich menu from a user

    Args:
        user_id: LINE user ID

    Returns:
        Success status
    """
    try:
        success = await service.unlink_rich_menu_from_user(user_id)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to unlink rich menu")

        return {"status": "success", "user_id": user_id}

    except Exception as e:
        logger.error(f"Unlink rich menu error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{rich_menu_id}")
async def delete_rich_menu(
    rich_menu_id: str,
    service: RichMenuService = Depends(get_rich_menu_svc)
):
    """
    Delete a rich menu

    Args:
        rich_menu_id: Rich menu ID

    Returns:
        Success status
    """
    try:
        success = await service.delete_rich_menu(rich_menu_id)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete rich menu")

        return {"status": "success", "rich_menu_id": rich_menu_id}

    except Exception as e:
        logger.error(f"Delete rich menu error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
