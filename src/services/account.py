# VoVoice Account Service
# Licensed under GNU GPLv3
# Copyright VoVoice 2026 Onwards

import secrets
import bcrypt
from datetime import datetime, timedelta
from database.db import db
from middleware.auth import generate_jwt


class AccountService:
    def create_account(self, email: str, password: str, display_name: str = None) -> dict:
        existing = db.get_user_by_email(email)
        if existing:
            raise ValueError("Email already registered")

        user_id = f"usr_{secrets.token_hex(8)}"
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()

        db.create_user(user_id, email, password_hash, display_name)

        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=24)
        db.create_verification_token(user_id, token, "email_verify", expires_at)

        return {"user_id": user_id, "verification_token": token}

    def login(self, email: str, password: str) -> dict:
        user = db.get_user_by_email(email)
        if not user:
            raise ValueError("Invalid credentials")

        if not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
            raise ValueError("Invalid credentials")

        if not user["email_verified"]:
            raise ValueError("Email not verified")

        if user.get("is_banned"):
            raise ValueError("Account banned")

        db.update_last_login(user["user_id"])
        token = generate_jwt(user["user_id"], days=7)

        return {
            "user_id": user["user_id"],
            "email": user["email"],
            "display_name": user.get("display_name"),
            "token": token,
            "expires_at": (datetime.now() + timedelta(days=7)).isoformat()
        }

    def verify_email(self, token: str) -> dict:
        token_data = db.get_verification_token(token)
        if not token_data:
            raise ValueError("Invalid or expired token")

        if token_data["expires_at"] < datetime.now().isoformat():
            raise ValueError("Token expired")

        if token_data["used"]:
            raise ValueError("Token already used")

        db.verify_user_email(token_data["user_id"])
        db.use_verification_token(token)

        return {"user_id": token_data["user_id"]}

    def get_devices(self, user_id: str) -> list:
        devices = db.get_devices_by_user(user_id)
        return [
            {
                "device_id": d["device_id"],
                "device_name": d["device_name"],
                "device_type": d["device_type"],
                "firmware_version": d["firmware_version"],
                "last_seen": d["last_seen"],
                "is_active": bool(d["is_active"])
            }
            for d in devices
        ]


account_service = AccountService()
