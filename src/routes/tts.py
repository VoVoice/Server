# VoVoice TTS Routes
# Licensed under GNU GPLv3
# Copyright VoVoice 2026 Onwards

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from models.schemas import TTSRequest
from middleware.auth import validate_device_key
from services.tts import tts_service

router = APIRouter()


@router.post("/tts")
async def text_to_speech(request: TTSRequest, device=Depends(validate_device_key)):
    try:
        audio_bytes = tts_service.synthesize(
            text=request.text,
            voice=request.voice,
            speed=request.speed,
            output_format=request.format
        )

        content_type = "audio/mpeg" if request.format == "mp3" else "audio/wav"

        return Response(
            content=audio_bytes,
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="speech.{request.format}"'
            }
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Synthesis failed: {str(e)}")


@router.get("/voices")
async def list_voices(device=Depends(validate_device_key)):
    voices = tts_service.get_available_voices()
    return {
        "voices": voices,
        "default": tts_service.default_voice or "en_US-lessac-medium"
    }
