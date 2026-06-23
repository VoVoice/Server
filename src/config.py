# VoVoice Configuration
# Licensed under GNU GPLv3
# Copyright VoVoice 2026 Onwards

import json
import os
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional


class ServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    name: str = "VoVoice Server"
    version: str = "1.0.0"
    cors_origins: List[str] = ["*"]
    rate_limit: str = "60/minute"
    debug: bool = False
    api_key: Optional[str] = None


class STTConfig(BaseModel):
    model: str = "base"
    device: str = "cpu"
    language: str = "en"
    beam_size: int = 5
    vad_filter: bool = True


class TTSConfig(BaseModel):
    default_voice: str = "en_US-lessac-medium"
    output_format: str = "wav"
    speed: float = 1.0
    voices_dir: str = "./data/voices"


class AIConfig(BaseModel):
    primary_model: str = "google/gemma-4-31b-it:free"
    backup_models: List[str] = [
        "openai/gpt-oss-120b:free",
        "google/gemma-4-26b-a4b-it:free",
        "liquid/lfm-2.5-1.2b-thinking:free",
        "poolside/laguna-xs.2:free",
    ]
    system_prompt: str = "You are Vo, a helpful voice assistant. Be concise and friendly."
    max_tokens: int = 1024
    temperature: float = 0.7
    timeout: int = 30


class SessionConfig(BaseModel):
    memory_messages: int = 5
    ttl_hours: int = 24
    storage: str = "sqlite"


class DatabaseConfig(BaseModel):
    type: str = "sqlite"
    path: str = "./data/vovoice.db"


class EmailConfig(BaseModel):
    enabled: bool = False
    smtp_host: str = "smtp.example.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    from_address: str = "noreply@vovoice.example.com"


class LoggingConfig(BaseModel):
    level: str = "INFO"
    file: str = "./data/logs/vovoice.log"
    max_size_mb: int = 10
    backup_count: int = 5


class AppConfig(BaseModel):
    server: ServerConfig = ServerConfig()
    stt: STTConfig = STTConfig()
    tts: TTSConfig = TTSConfig()
    ai: AIConfig = AIConfig()
    session: SessionConfig = SessionConfig()
    database: DatabaseConfig = DatabaseConfig()
    email: EmailConfig = EmailConfig()
    logging: LoggingConfig = LoggingConfig()
    openrouter_token: str = ""


def load_config(path: str = "config.json") -> AppConfig:
    """Load configuration from file with environment variable overrides."""
    config_path = Path(path)

    if config_path.exists():
        with open(config_path) as f:
            data = json.load(f)
    else:
        data = {}

    env_overrides = {
        "OPENROUTER_TOKEN": ("openrouter_token", str),
        "SERVER_API_KEY": ("server.api_key", str),
        "SERVER_HOST": ("server.host", str),
        "SERVER_PORT": ("server.port", int),
        "STT_MODEL": ("stt.model", str),
        "STT_DEVICE": ("stt.device", str),
        "TTS_VOICE": ("tts.default_voice", str),
        "DATABASE_PATH": ("database.path", str),
        "LOG_LEVEL": ("logging.level", str),
        "DOMAIN": ("domain", str),
        "JWT_SECRET": ("jwt_secret", str),
        "SMTP_HOST": ("email.smtp_host", str),
        "SMTP_PORT": ("email.smtp_port", int),
        "SMTP_USER": ("email.smtp_user", str),
        "SMTP_PASSWORD": ("email.smtp_password", str),
    }

    for env_key, (config_path_str, config_type) in env_overrides.items():
        env_value = os.getenv(env_key)
        if env_value:
            keys = config_path_str.split(".")
            obj = data
            for key in keys[:-1]:
                if key not in obj:
                    obj[key] = {}
                obj = obj[key]
            obj[keys[-1]] = config_type(env_value)

    return AppConfig(**data)
