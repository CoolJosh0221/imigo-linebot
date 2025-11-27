"""System and health check endpoints"""
import logging
from fastapi import APIRouter, Depends
from datetime import datetime

from config import get_config
from dependencies import get_database_service

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
    cfg = get_config()
    return {
        "bot": {
            "name": cfg.name,
            "language": cfg.language,
            "country": cfg.country,
        },
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/stats")
async def get_stats(db_service = Depends(get_database_service)):
    """
    Get basic statistics about the service

    Returns:
        Service statistics
    """
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
