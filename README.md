# VOServer

Self-hosted voice assistant server for VoVoice.

## Features

- **STT**: Local speech-to-text via faster-whisper
- **TTS**: Local text-to-speech via Piper
- **AI**: OpenRouter integration with automatic model fallback
- **Auth**: User accounts + device API keys
- **Memory**: Session-based conversation memory
- **Docker**: Single container deployment

## Quick Start

### 1. Clone and Configure

```bash
git clone https://github.com/yourusername/VoVoice.git
cd VoVoice/VOServer
cp .env.example .env
# Edit .env with your OpenRouter token
```

### 2. Run with Docker

```bash
docker compose up -d
```

### 3. Verify

```bash
curl http://localhost:8000/health
```

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | No | Server info |
| POST | `/health` | No | Health check |
| POST | `/account/register` | No | Create account |
| POST | `/account/login` | No | Login |
| POST | `/account/verify` | No | Verify email |
| GET | `/account/devices` | JWT | List devices |
| POST | `/auth/register` | Creds | Register device |
| POST | `/auth/login` | Key | Device login |
| POST | `/stt` | Key | Transcribe audio |
| POST | `/chat` | Key | AI chat |
| POST | `/tts` | Key | Text-to-speech |
| GET | `/config` | Key | Get config |
| GET | `/models` | Key | List models |
| GET | `/voices` | Key | List voices |

## Configuration

Edit `config.json` or use environment variables:

```bash
export OPENROUTER_TOKEN=sk-or-v1-your_token
export JWT_SECRET=your_secret
```

## Development

```bash
pip install -r requirements.txt
uvicorn src.main:app --reload
```

## License

GNU GPLv3
