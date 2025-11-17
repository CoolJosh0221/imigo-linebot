"""System and health check endpoints"""
import logging
from fastapi import APIRouter
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/system", tags=["System"])


@router.get("/health")
async def health_check():
    """
    Health check endpoint

    Returns:
        Health status and timestamp
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "imigo-linebot",
    }


@router.get("/info")
async def system_info():
    """
    Get system information about the bot

    Returns:
        Bot configuration and system details
    """
    from main import get_config

    cfg = get_config()
    return {
        "bot": {
            "name": cfg.bot.name,
            "language": cfg.bot.language,
            "country": cfg.bot.country,
        },
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/stats")
async def get_stats():
    """
    Get basic statistics about the service

    Returns:
        Service statistics
    """
    from main import db_service

    try:
        # You can add more statistics here as needed
        return {
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }
