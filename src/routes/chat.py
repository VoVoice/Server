# VoVoice Chat Routes
# Licensed under GNU GPLv3
# Copyright VoVoice 2026 Onwards

from fastapi import APIRouter, Depends, HTTPException
from models.schemas import ChatRequest
from middleware.auth import validate_device_key
from services.ai import ai_service
from services.session import session_service

router = APIRouter()


@router.post("/chat")
async def chat(request: ChatRequest, device=Depends(validate_device_key)):
    try:
        session_memory = session_service.get_memory(request.session_id)

        messages = [{"role": "user", "content": request.text}]

        response_text, model_used = ai_service.chat(
            messages=messages,
            session_memory=session_memory if session_memory else None
        )

        session_service.add_message(
            session_id=request.session_id,
            device_id=device["device_id"],
            role="user",
            content=request.text
        )

        session_service.add_message(
            session_id=request.session_id,
            device_id=device["device_id"],
            role="assistant",
            content=response_text
        )

        return {
            "status": "success",
            "response": response_text,
            "model_used": model_used,
            "session_id": request.session_id
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"AI service error: {str(e)}")


@router.post("/session/clear")
async def clear_session(request: dict, device=Depends(validate_device_key)):
    session_id = request.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="Missing session_id")

    count = session_service.clear_session(session_id)

    return {
        "status": "cleared",
        "session_id": session_id,
        "messages_deleted": count
    }
