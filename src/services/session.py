# VoVoice Session Service
# Licensed under GNU GPLv3
# Copyright VoVoice 2026 Onwards

from datetime import datetime, timedelta
from database.db import db


class SessionService:
    def __init__(self):
        self.max_messages = 5
        self.ttl_hours = 24

    def configure(self, config):
        self.max_messages = config.session.memory_messages
        self.ttl_hours = config.session.ttl_hours

    def get_memory(self, session_id: str) -> list:
        return db.get_session_memory(session_id, self.max_messages)

    def add_message(self, session_id: str, device_id: str, role: str, content: str):
        expires_at = datetime.now() + timedelta(hours=self.ttl_hours)
        db.add_session_message(session_id, device_id, role, content, expires_at)

    def clear_session(self, session_id: str) -> int:
        with db.connection() as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) as count FROM sessions WHERE session_id = ?", (session_id,)
            )
            count = cursor.fetchone()["count"]
            db.clear_session(session_id)
            return count

    def cleanup_expired(self):
        db.cleanup_expired_sessions()

    def get_stats(self) -> dict:
        return {
            "active_sessions": db.get_active_sessions_count(),
            "max_messages": self.max_messages,
            "ttl_hours": self.ttl_hours
        }


session_service = SessionService()
