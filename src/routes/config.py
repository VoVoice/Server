# VoVoice Config Routes
# Licensed under GNU GPLv3
# Copyright VoVoice 2026 Onwards

from fastapi import APIRouter, Depends
from middleware.auth import validate_device_key
from services.ai import ai_service
from config import load_config

config = load_config()

router = APIRouter()


@router.get("/config")
async def get_config(device=Depends(validate_device_key)):
    return {
        "server": {
            "version": config.server.version,
            "name": config.server.name
        },
        "stt": {
            "model": config.stt.model,
            "device": config.stt.device,
            "language": config.stt.language
        },
        "tts": {
            "default_voice": config.tts.default_voice,
            "output_format": config.tts.output_format,
            "speed": config.tts.speed
        },
        "ai": {
            "primary_model": config.ai.primary_model,
            "backup_models": config.ai.backup_models,
            "system_prompt": config.ai.system_prompt,
            "max_tokens": config.ai.max_tokens,
            "temperature": config.ai.temperature
        },
        "session": {
            "memory_messages": config.session.memory_messages,
            "ttl_hours": config.session.ttl_hours
        }
    }


@router.get("/models")
async def list_models(device=Depends(validate_device_key)):
    return {"models": ai_service.get_models_list()}
