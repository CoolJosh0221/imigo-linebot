"""Chat API endpoints for direct interaction with the bot"""
import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

from dependencies import (
    get_ai_service,
    get_database_service,
    get_language_detection_service,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    user_id: str
    message: str
    language: Optional[str] = "auto"  # "auto" for auto-detection, or specific language code


class ChatResponse(BaseModel):
    user_id: str
    message: str
    response: str
    language: str


class ClearChatRequest(BaseModel):
    user_id: str


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    ai_service = Depends(get_ai_service),
    db_service = Depends(get_database_service),
    language_detection_service = Depends(get_language_detection_service)
):
    """
    Send a message to the bot and get a response

    Args:
        request: Chat request with user_id, message, and optional language
                 Set language to "auto" (default) for automatic language detection

    Returns:
        ChatResponse with the bot's reply and detected/used language
    """
    try:
        # Detect language if set to "auto" or not provided
        detected_language = request.language
        if not request.language or request.language == "auto":
            detected_language = language_detection_service.detect_language(request.message)
            logger.info(f"Auto-detected language: {detected_language} for user {request.user_id[:8]}")

        # Set user language if detected/provided
        current_lang = await db_service.get_user_language(request.user_id)
        if not current_lang or current_lang != detected_language:
            await db_service.set_user_language(request.user_id, detected_language)
            logger.info(f"Updated user {request.user_id[:8]} language to: {detected_language}")

        # Generate response
        response = await ai_service.generate_response(request.user_id, request.message)

        return ChatResponse(
            user_id=request.user_id,
            message=request.message,
            response=response,
            language=detected_language,
        )
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear")
async def clear_conversation(
    request: ClearChatRequest,
    db_service = Depends(get_database_service)
):
    """
    Clear conversation history for a user

    Args:
        request: Request with user_id

    Returns:
        Success message
    """
    try:
        await db_service.clear_user_conversation(request.user_id)
        return {"status": "success", "message": "Conversation cleared"}
    except Exception as e:
        logger.error(f"Clear conversation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{user_id}")
async def get_conversation_history(
    user_id: str,
    limit: int = 10,
    db_service = Depends(get_database_service)
):
    """
    Get conversation history for a user

    Args:
        user_id: User identifier
        limit: Maximum number of messages to return (default: 10)

    Returns:
        List of conversation messages
    """
    try:
        history = await db_service.get_conversation_history(user_id, limit)
        return {"user_id": user_id, "history": history, "count": len(history)}
    except Exception as e:
        logger.error(f"Get history error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
