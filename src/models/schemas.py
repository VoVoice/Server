# VoVoice Pydantic Models
# Licensed under GNU GPLv3
# Copyright VoVoice 2026 Onwards

from pydantic import BaseModel, Field, validator
from typing import Optional, List
import re


class AccountRegisterRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=256)
    password: str = Field(..., min_length=8, max_length=128)
    display_name: Optional[str] = Field(None, max_length=128)

    @validator("email")
    def validate_email(cls, v):
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", v):
            raise ValueError("Invalid email format")
        return v.lower()

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain an uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain a lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain a number")
        return v


class AccountLoginRequest(BaseModel):
    email: str
    password: str


class AccountVerifyRequest(BaseModel):
    token: str


class DeviceRegisterRequest(BaseModel):
    device_id: str = Field(..., min_length=1, max_length=64)
    device_name: str = Field(..., min_length=1, max_length=128)
    device_type: str = Field(default="esp32s3", max_length=32)
    firmware_version: str = Field(..., max_length=32)
    account_email: str
    account_password: str

    @validator("device_id")
    def validate_device_id(cls, v):
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Invalid device ID format")
        return v


class DeviceLoginRequest(BaseModel):
    device_id: str
    firmware_version: str


class STTRequest(BaseModel):
    language: str = Field(default="en", max_length=10)


class ChatRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=4096)
    session_id: str = Field(..., min_length=1, max_length=128)
    voice: Optional[str] = Field(None, max_length=64)

    @validator("session_id")
    def validate_session_id(cls, v):
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Invalid session ID format")
        return v

    @validator("text")
    def validate_text(cls, v):
        v = " ".join(v.split())
        if not v:
            raise ValueError("Text cannot be empty")
        return v


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=4096)
    voice: Optional[str] = Field(None, max_length=64)
    speed: float = Field(default=1.0, ge=0.5, le=2.0)
    format: str = Field(default="wav", pattern="^(wav|mp3)$")


class SessionClearRequest(BaseModel):
    session_id: str


class RotateKeyRequest(BaseModel):
    device_id: str


class SuccessResponse(BaseModel):
    status: str = "success"
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    status: str = "error"
    error: str
    detail: Optional[str] = None
