# VoVoice STT Service
# Licensed under GNU GPLv3
# Copyright VoVoice 2026 Onwards

import io
import tempfile
from pathlib import Path


class STTService:
    def __init__(self):
        self.model = None
        self.model_size = None
        self.device = None

    def _load_model(self, model_size: str, device: str):
        if self.model is None or self.model_size != model_size or self.device != device:
            from faster_whisper import WhisperModel
            self.model = WhisperModel(model_size, device=device)
            self.model_size = model_size
            self.device = device

    def transcribe(self, audio_bytes: bytes, language: str = "en",
                   model_size: str = "base", device: str = "cpu") -> dict:
        self._load_model(model_size, device)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        try:
            segments, info = self.model.transcribe(
                tmp_path,
                language=language if language != "auto" else None,
                beam_size=5,
                vad_filter=True
            )

            text = "".join([seg.text for seg in segments])

            return {
                "text": text.strip(),
                "language": info.language,
                "duration": info.duration,
                "confidence": info.language_probability
            }
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def get_health(self) -> dict:
        return {
            "status": "ready" if self.model else "standby",
            "model": self.model_size or "not_loaded",
            "device": self.device or "not_loaded"
        }


stt_service = STTService()
