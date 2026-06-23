# VoVoice Device Service
# Licensed under GNU GPLv3
# Copyright VoVoice 2026 Onwards

import secrets
import bcrypt
from database.db import db


class DeviceService:
    def register_device(self, device_id: str, device_name: str, device_type: str,
                        firmware_version: str, account_email: str, account_password: str) -> dict:
        user = db.get_user_by_email(account_email)
        if not user:
            raise ValueError("Invalid credentials")

        if not bcrypt.checkpw(account_password.encode(), user["password_hash"].encode()):
            raise ValueError("Invalid credentials")

        if not user["email_verified"]:
            raise ValueError("Email not verified")

        existing = db.get_device_by_id(device_id)
        if existing:
            raise ValueError("Device already registered")

        device_key = f"vvk_{secrets.token_urlsafe(32)}"

        db.create_device(
            device_id=device_id,
            device_key=device_key,
            device_name=device_name,
            device_type=device_type,
            firmware_version=firmware_version,
            user_id=user["user_id"]
        )

        return {
            "device_id": device_id,
            "device_key": device_key,
            "device_name": device_name,
            "user_id": user["user_id"]
        }

    def login_device(self, device_id: str, firmware_version: str) -> dict:
        device = db.get_device_by_id(device_id)
        if not device:
            raise ValueError("Device not found")

        if device.get("is_banned"):
            raise ValueError("Device banned")

        if not device.get("is_active"):
            raise ValueError("Device inactive")

        db.update_device_last_seen(device_id)

        return {
            "device_id": device["device_id"],
            "device_name": device["device_name"],
            "device_type": device["device_type"],
            "user_id": device["user_id"]
        }

    def rotate_key(self, device_id: str) -> dict:
        device = db.get_device_by_id(device_id)
        if not device:
            raise ValueError("Device not found")

        new_key = f"vvk_{secrets.token_urlsafe(32)}"

        with db.connection() as conn:
            conn.execute("UPDATE devices SET device_key = ? WHERE device_id = ?", (new_key, device_id))

        return {
            "device_id": device_id,
            "new_device_key": new_key
        }


device_service = DeviceService()
