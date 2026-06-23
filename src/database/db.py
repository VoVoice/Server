# VoVoice Database
# Licensed under GNU GPLv3
# Copyright VoVoice 2026 Onwards

import sqlite3
import os
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime


class Database:
    def __init__(self, db_path: str = "./data/vovoice.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        try:
            yield conn
        finally:
            conn.close()

    def init_tables(self):
        with self.connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    email_verified BOOLEAN DEFAULT 0,
                    password_hash TEXT NOT NULL,
                    display_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    is_banned BOOLEAN DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS devices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT UNIQUE NOT NULL,
                    device_key TEXT UNIQUE NOT NULL,
                    device_name TEXT,
                    device_type TEXT DEFAULT 'esp32s3',
                    firmware_version TEXT,
                    user_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    is_banned BOOLEAN DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );

                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    device_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (device_id) REFERENCES devices(device_id)
                );

                CREATE TABLE IF NOT EXISTS verification_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    token_type TEXT NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    used BOOLEAN DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );

                CREATE INDEX IF NOT EXISTS idx_user_id ON users(user_id);
                CREATE INDEX IF NOT EXISTS idx_user_email ON users(email);
                CREATE INDEX IF NOT EXISTS idx_device_key ON devices(device_key);
                CREATE INDEX IF NOT EXISTS idx_device_id ON devices(device_id);
                CREATE INDEX IF NOT EXISTS idx_device_user ON devices(user_id);
                CREATE INDEX IF NOT EXISTS idx_session_id ON sessions(session_id);
                CREATE INDEX IF NOT EXISTS idx_session_expires ON sessions(expires_at);
                CREATE INDEX IF NOT EXISTS idx_verification_token ON verification_tokens(token);
            """)

    def get_user_by_email(self, email: str):
        with self.connection() as conn:
            row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
            return dict(row) if row else None

    def get_user_by_id(self, user_id: str):
        with self.connection() as conn:
            row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
            return dict(row) if row else None

    def create_user(self, user_id: str, email: str, password_hash: str, display_name: str = None):
        with self.connection() as conn:
            conn.execute(
                "INSERT INTO users (user_id, email, password_hash, display_name) VALUES (?, ?, ?, ?)",
                (user_id, email, password_hash, display_name)
            )

    def verify_user_email(self, user_id: str):
        with self.connection() as conn:
            conn.execute("UPDATE users SET email_verified = 1 WHERE user_id = ?", (user_id,))

    def update_last_login(self, user_id: str):
        with self.connection() as conn:
            conn.execute("UPDATE users SET last_login = ? WHERE user_id = ?", (datetime.now(), user_id))

    def create_verification_token(self, user_id: str, token: str, token_type: str, expires_at: datetime):
        with self.connection() as conn:
            conn.execute(
                "INSERT INTO verification_tokens (user_id, token, token_type, expires_at) VALUES (?, ?, ?, ?)",
                (user_id, token, token_type, expires_at)
            )

    def get_verification_token(self, token: str):
        with self.connection() as conn:
            row = conn.execute(
                "SELECT * FROM verification_tokens WHERE token = ? AND used = 0", (token,)
            ).fetchone()
            return dict(row) if row else None

    def use_verification_token(self, token: str):
        with self.connection() as conn:
            conn.execute("UPDATE verification_tokens SET used = 1 WHERE token = ?", (token,))

    def get_device_by_key(self, device_key: str):
        with self.connection() as conn:
            row = conn.execute("SELECT * FROM devices WHERE device_key = ?", (device_key,)).fetchone()
            return dict(row) if row else None

    def get_device_by_id(self, device_id: str):
        with self.connection() as conn:
            row = conn.execute("SELECT * FROM devices WHERE device_id = ?", (device_id,)).fetchone()
            return dict(row) if row else None

    def get_devices_by_user(self, user_id: str):
        with self.connection() as conn:
            rows = conn.execute("SELECT * FROM devices WHERE user_id = ?", (user_id,)).fetchall()
            return [dict(row) for row in rows]

    def create_device(self, device_id: str, device_key: str, device_name: str,
                      device_type: str, firmware_version: str, user_id: str):
        with self.connection() as conn:
            conn.execute(
                "INSERT INTO devices (device_id, device_key, device_name, device_type, firmware_version, user_id) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (device_id, device_key, device_name, device_type, firmware_version, user_id)
            )

    def update_device_last_seen(self, device_id: str):
        with self.connection() as conn:
            conn.execute("UPDATE devices SET last_seen = ? WHERE device_id = ?", (datetime.now(), device_id))

    def add_session_message(self, session_id: str, device_id: str, role: str, content: str, expires_at: datetime):
        with self.connection() as conn:
            conn.execute(
                "INSERT INTO sessions (session_id, device_id, role, content, expires_at) VALUES (?, ?, ?, ?, ?)",
                (session_id, device_id, role, content, expires_at)
            )

    def get_session_memory(self, session_id: str, limit: int = 5):
        with self.connection() as conn:
            rows = conn.execute(
                "SELECT role, content FROM sessions WHERE session_id = ? AND expires_at > ? "
                "ORDER BY created_at DESC LIMIT ?",
                (session_id, datetime.now(), limit)
            ).fetchall()
            return [{"role": row["role"], "content": row["content"]} for row in reversed(rows)]

    def clear_session(self, session_id: str):
        with self.connection() as conn:
            conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))

    def cleanup_expired_sessions(self):
        with self.connection() as conn:
            conn.execute("DELETE FROM sessions WHERE expires_at < ?", (datetime.now(),))

    def get_active_sessions_count(self):
        with self.connection() as conn:
            row = conn.execute("SELECT COUNT(DISTINCT session_id) as count FROM sessions WHERE expires_at > ?",
                             (datetime.now(),)).fetchone()
            return row["count"] if row else 0


db = Database()
