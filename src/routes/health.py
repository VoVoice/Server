# VoVoice Health Routes
# Licensed under GNU GPLv3
# Copyright VoVoice 2026 Onwards

import time
from fastapi import APIRouter, Request
from services.stt import stt_service
from services.tts import tts_service
from services.ai import ai_service
from services.session import session_service

router = APIRouter()

start_time = time.time()


@router.get("/")
async def root():
    return {
        "name": "VoVoice Server",
        "version": "1.0.0",
        "status": "online"
    }


@router.post("/health")
async def health_check():
    uptime = int(time.time() - start_time)

    stt_health = stt_service.get_health()
    tts_health = tts_service.get_health()
    ai_health = ai_service.get_health()
    session_stats = session_service.get_stats()

    overall_status = "healthy"
    if ai_health["status"] != "ready":
        overall_status = "degraded"

    return {
        "status": overall_status,
        "server": {
            "version": "1.0.0",
            "uptime": uptime
        },
        "stt": stt_health,
        "tts": tts_health,
        "ai": ai_health,
        "database": {
            "status": "connected",
            "type": "sqlite",
            "sessions_active": session_stats["active_sessions"]
        }
    }
