# VoVoice Audio Utilities
# Licensed under GNU GPLv3
# Copyright VoVoice 2026 Onwards

import wave
import io
from typing import Optional


def validate_wav_header(audio_bytes: bytes) -> bool:
    try:
        with io.BytesIO(audio_bytes) as buf:
            with wave.open(buf, 'rb') as wav:
                params = wav.getparams()
                return params.nchannels > 0 and params.sampwidth > 0 and params.framerate > 0
    except Exception:
        return False


def get_wav_duration(audio_bytes: bytes) -> float:
    try:
        with io.BytesIO(audio_bytes) as buf:
            with wave.open(buf, 'rb') as wav:
                frames = wav.getnframes()
                rate = wav.getframerate()
                return frames / float(rate)
    except Exception:
        return 0.0


def convert_pcm_to_wav(pcm_data: bytes, sample_rate: int = 22050,
                        channels: int = 1, sample_width: int = 2) -> bytes:
    with io.BytesIO() as buf:
        with wave.open(buf, 'wb') as wav:
            wav.setnchannels(channels)
            wav.setsampwidth(sample_width)
            wav.setframerate(sample_rate)
            wav.writeframes(pcm_data)
        return buf.getvalue()
