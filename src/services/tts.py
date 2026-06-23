# VoVoice TTS Service
# Licensed under GNU GPLv3
# Copyright VoVoice 2026 Onwards

import io
import wave
from pathlib import Path


class TTSService:
    def __init__(self):
        self.voices = {}
        self.default_voice = None

    def _load_voice(self, voice_name: str):
        if voice_name not in self.voices:
            from piper import PiperVoice
            voice_path = f"data/voices/{voice_name}.onnx"
            if not Path(voice_path).exists():
                raise FileNotFoundError(f"Voice model not found: {voice_name}")
            self.voices[voice_name] = PiperVoice.load(voice_path)
        return self.voices[voice_name]

    def synthesize(self, text: str, voice: str = None, speed: float = 1.0,
                   output_format: str = "wav") -> bytes:
        voice_name = voice or self.default_voice or "en_US-lessac-medium"
        piper_voice = self._load_voice(voice_name)

        audio_buffer = io.BytesIO()

        with wave.open(audio_buffer, "wb") as wav_file:
            piper_voice.synthesize_wav(text, wav_file)

        audio_bytes = audio_buffer.getvalue()

        if output_format == "mp3":
            audio_bytes = self._convert_to_mp3(audio_bytes)

        return audio_bytes

    def _convert_to_mp3(self, wav_bytes: bytes) -> bytes:
        import subprocess
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_file:
            wav_file.write(wav_bytes)
            wav_path = wav_file.name

        mp3_path = wav_path.replace(".wav", ".mp3")

        try:
            subprocess.run(
                ["ffmpeg", "-i", wav_path, "-codec:a", "libmp3lame", "-qscale:a", "2", mp3_path, "-y"],
                check=True,
                capture_output=True
            )
            with open(mp3_path, "rb") as f:
                return f.read()
        finally:
            Path(wav_path).unlink(missing_ok=True)
            Path(mp3_path).unlink(missing_ok=True)

    def get_available_voices(self) -> list:
        voices_dir = Path("data/voices")
        if not voices_dir.exists():
            return []

        voices = []
        for voice_file in voices_dir.glob("*.onnx"):
            voice_name = voice_file.stem
            parts = voice_name.split("-")
            if len(parts) >= 2:
                lang = parts[0]
                name = "-".join(parts[1:])
            else:
                lang = "unknown"
                name = voice_name

            voices.append({
                "name": voice_name,
                "language": lang,
                "file": str(voice_file)
            })

        return voices

    def get_health(self) -> dict:
        voices = self.get_available_voices()
        return {
            "status": "ready" if voices else "no_voices",
            "default_voice": self.default_voice or "en_US-lessac-medium",
            "voices_loaded": len(self.voices),
            "voices_available": len(voices)
        }


tts_service = TTSService()
