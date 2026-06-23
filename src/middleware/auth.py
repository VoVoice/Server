# VoVoice Authentication Middleware
# Licensed under GNU GPLv3
# Copyright VoVoice 2026 Onwards

import hashlib
import os
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from database.db import db


SECRET_KEY = os.getenv("JWT_SECRET", "vovoice-default-secret-change-in-production")
ALGORITHM = "HS256"

security = HTTPBearer(auto_error=False)


def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()


def generate_jwt(user_id: str, days: int = 7) -> str:
    expires = datetime.utcnow() + timedelta(days=days)
    payload = {"user_id": user_id, "exp": expires}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_jwt(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


async def validate_device_key(request: Request):
    api_key = request.headers.get("X-Device-Key")
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API key")

    device = db.get_device_by_key(api_key)
    if not device:
        raise HTTPException(status_code=401, detail="Invalid API key")

    if device.get("is_banned"):
        raise HTTPException(status_code=403, detail="Device banned")

    if not device.get("is_active"):
        raise HTTPException(status_code=403, detail="Device inactive")

    db.update_device_last_seen(device["device_id"])
    request.state.device = device
    return device


async def validate_user_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing authorization token")

    payload = decode_jwt(credentials.credentials)
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if user.get("is_banned"):
        raise HTTPException(status_code=403, detail="User banned")

    if not user.get("is_active"):
        raise HTTPException(status_code=403, detail="User inactive")

    return user


async def optional_device_key(request: Request):
    api_key = request.headers.get("X-Device-Key")
    if not api_key:
        return None

    device = db.get_device_by_key(api_key)
    if device and not device.get("is_banned"):
        db.update_device_last_seen(device["device_id"])
        request.state.device = device
        return device

    return None
