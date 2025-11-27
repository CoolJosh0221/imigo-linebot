"""Translation API endpoints"""
import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from dependencies import get_translation_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/translate", tags=["Translation"])


class TranslationRequest(BaseModel):
    text: str
    target_language: str
    source_language: str = "auto"


class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    source_language: str
    target_language: str


@router.post("/", response_model=TranslationResponse)
async def translate_text(
    request: TranslationRequest,
    translation_service = Depends(get_translation_service)
):
    """
    Translate text from one language to another

    Args:
        request: Translation request with text and language codes

    Returns:
        TranslationResponse with original and translated text

    Supported languages:
        - id: Indonesian (Bahasa Indonesia)
        - zh: Traditional Chinese (繁體中文)
        - en: English
        - vi: Vietnamese (Tiếng Việt)
        - th: Thai (ภาษาไทย)
        - fil: Tagalog (Filipino)
    """
    try:
        translated = await translation_service.translate_message(
            request.text, request.target_language, request.source_language
        )

        return TranslationResponse(
            original_text=request.text,
            translated_text=translated,
            source_language=request.source_language,
            target_language=request.target_language,
        )
    except Exception as e:
        logger.error(f"Translation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/languages")
async def get_supported_languages():
    """
    Get list of supported languages

    Returns:
        Dictionary of language codes and their names
    """
    return {
        "languages": {
            "id": "Indonesian (Bahasa Indonesia)",
            "zh": "Traditional Chinese (繁體中文)",
            "en": "English",
            "vi": "Vietnamese (Tiếng Việt)",
            "th": "Thai (ภาษาไทย)",
            "fil": "Tagalog (Filipino)",
        }
    }
