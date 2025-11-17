"""Chat API endpoints for direct interaction with the bot"""
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    user_id: str
    message: str
    language: str = "id"


class ChatResponse(BaseModel):
    user_id: str
    message: str
    response: str
    language: str


class ClearChatRequest(BaseModel):
    user_id: str


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    Send a message to the bot and get a response

    Args:
        request: Chat request with user_id, message, and optional language

    Returns:
        ChatResponse with the bot's reply
    """
    from main import ai_service, db_service

    try:
        # Set user language if provided
        current_lang = await db_service.get_user_language(request.user_id)
        if not current_lang or current_lang != request.language:
            await db_service.set_user_language(request.user_id, request.language)

        # Generate response
        response = await ai_service.generate_response(request.user_id, request.message)

        return ChatResponse(
            user_id=request.user_id,
            message=request.message,
            response=response,
            language=request.language,
        )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear")
async def clear_conversation(request: ClearChatRequest):
    """
    Clear conversation history for a user

    Args:
        request: Request with user_id

    Returns:
        Success message
    """
    from main import db_service

    try:
        await db_service.clear_user_conversation(request.user_id)
        return {"status": "success", "message": "Conversation cleared"}
    except Exception as e:
        logger.error(f"Clear conversation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{user_id}")
async def get_conversation_history(user_id: str, limit: int = 10):
    """
    Get conversation history for a user

    Args:
        user_id: User identifier
        limit: Maximum number of messages to return (default: 10)

    Returns:
        List of conversation messages
    """
    from main import db_service

    try:
        history = await db_service.get_conversation_history(user_id, limit)
        return {"user_id": user_id, "history": history, "count": len(history)}
    except Exception as e:
        logger.error(f"Get history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
