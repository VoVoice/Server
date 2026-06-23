# VoVoice Account Routes
# Licensed under GNU GPLv3
# Copyright VoVoice 2026 Onwards

from fastapi import APIRouter, Depends, HTTPException
from models.schemas import (
    AccountRegisterRequest, AccountLoginRequest, AccountVerifyRequest
)
from services.account import account_service
from middleware.auth import validate_user_token

router = APIRouter(prefix="/account")


@router.post("/register")
async def register_account(request: AccountRegisterRequest):
    try:
        result = account_service.create_account(
            email=request.email,
            password=request.password,
            display_name=request.display_name
        )
        return {
            "status": "registered",
            "user_id": result["user_id"],
            "email": request.email,
            "message": "Check your email to verify your account"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
async def login_account(request: AccountLoginRequest):
    try:
        result = account_service.login(
            email=request.email,
            password=request.password
        )
        return {
            "status": "authenticated",
            **result
        }
    except ValueError as e:
        status_code = 403 if "not verified" in str(e).lower() else 401
        raise HTTPException(status_code=status_code, detail=str(e))


@router.post("/verify")
async def verify_account(request: AccountVerifyRequest):
    try:
        result = account_service.verify_email(token=request.token)
        return {
            "status": "verified",
            "user_id": result["user_id"],
            "message": "Email verified successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/devices")
async def list_devices(user=Depends(validate_user_token)):
    devices = account_service.get_devices(user["user_id"])
    return {"devices": devices}


@router.post("/logout")
async def logout_account(user=Depends(validate_user_token)):
    return {
        "status": "logged_out",
        "message": "Token invalidated"
    }
