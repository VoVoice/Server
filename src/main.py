# VoVoice Server
# Licensed under GNU GPLv3
# Copyright VoVoice 2026 Onwards

import os
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import load_config
from database.db import db
from middleware.rate_limit import setup_rate_limiting
from services.stt import stt_service
from services.tts import tts_service
from services.ai import ai_service
from services.session import session_service
from routes import health, account, auth, stt, chat, tts, config as config_routes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vovoice")

config = load_config()

app = FastAPI(
    title="VoVoice Server",
    description="Self-hosted voice assistant server",
    version=config.server.version,
    docs_url="/docs" if config.server.debug else None,
    redoc_url="/redoc" if config.server.debug else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.server.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
)

setup_rate_limiting(app, config.server.rate_limit)


@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


@app.on_event("startup")
async def startup():
    logger.info("Starting VoVoice Server...")

    Path(config.database.path).parent.mkdir(parents=True, exist_ok=True)
    Path(config.tts.voices_dir).mkdir(parents=True, exist_ok=True)
    Path("./data/logs").mkdir(parents=True, exist_ok=True)

    db.init_tables()
    logger.info("Database initialized")

    ai_service.configure(config)
    session_service.configure(config)
    tts_service.default_voice = config.tts.default_voice

    logger.info(f"Server ready on {config.server.host}:{config.server.port}")


@app.on_event("shutdown")
async def shutdown():
    logger.info("Shutting down VoVoice Server...")


app.include_router(health.router)
app.include_router(account.router)
app.include_router(auth.router)
app.include_router(stt.router)
app.include_router(chat.router)
app.include_router(tts.router)
app.include_router(config_routes.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=config.server.host,
        port=config.server.port,
        reload=config.server.debug
    )
