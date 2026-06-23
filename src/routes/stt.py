# VoVoice STT Routes
# Licensed under GNU GPLv3
# Copyright VoVoice 2026 Onwards

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from middleware.auth import validate_device_key
from services.stt import stt_service
from config import load_config

config = load_config()

router = APIRouter()

ALLOWED_AUDIO_TYPES = ["audio/wav", "audio/mpeg", "audio/ogg", "audio/flac", "audio/x-wav"]
MAX_AUDIO_SIZE = 25 * 1024 * 1024


@router.post("/stt")
async def transcribe_audio(
    audio: UploadFile = File(...),
    language: str = Form(default="en"),
    device=Depends(validate_device_key)
):
    if audio.content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid audio type: {audio.content_type}")

    contents = await audio.read()
    if len(contents) > MAX_AUDIO_SIZE:
        raise HTTPException(status_code=413, detail=f"Audio too large: {len(contents)} bytes")

    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Empty audio file")

    try:
        result = stt_service.transcribe(
            audio_bytes=contents,
            language=language,
            model_size=config.stt.model,
            device=config.stt.device
        )
        return {
            "status": "transcribed",
            "text": result["text"],
            "language": result["language"],
            "duration": result["duration"],
            "confidence": result["confidence"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
