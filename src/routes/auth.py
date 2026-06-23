# VoVoice Device Auth Routes
# Licensed under GNU GPLv3
# Copyright VoVoice 2026 Onwards

from fastapi import APIRouter, Depends, HTTPException, Request
from models.schemas import DeviceRegisterRequest, DeviceLoginRequest, RotateKeyRequest
from services.device import device_service
from middleware.auth import validate_device_key

router = APIRouter(prefix="/auth")


@router.post("/register")
async def register_device(request: DeviceRegisterRequest):
    try:
        result = device_service.register_device(
            device_id=request.device_id,
            device_name=request.device_name,
            device_type=request.device_type,
            firmware_version=request.firmware_version,
            account_email=request.account_email,
            account_password=request.account_password
        )
        return {
            "status": "registered",
            "device_id": result["device_id"],
            "device_key": result["device_key"],
            "message": "Device registered successfully"
        }
    except ValueError as e:
        status_code = 409 if "already registered" in str(e).lower() else 401
        raise HTTPException(status_code=status_code, detail=str(e))


@router.post("/login")
async def login_device(request: DeviceLoginRequest, device=Depends(validate_device_key)):
    try:
        result = device_service.login_device(
            device_id=request.device_id,
            firmware_version=request.firmware_version
        )
        return {
            "status": "authenticated",
            **result
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/rotate-key")
async def rotate_device_key(request: RotateKeyRequest, device=Depends(validate_device_key)):
    try:
        result = device_service.rotate_key(device_id=request.device_id)
        return {
            "status": "rotated",
            "new_device_key": result["new_device_key"],
            "message": "Key rotated successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
