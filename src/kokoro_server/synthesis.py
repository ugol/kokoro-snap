"""Audio generation; all models and dependencies are loaded locally."""
import io
import os
import wave
from functools import lru_cache

import numpy as np

MODEL_PATH = os.environ.get("KOKORO_MODEL_PATH", "models/kokoro-v1.0.onnx")
VOICES_PATH = os.environ.get("KOKORO_VOICES_PATH", "models/voices-v1.0.bin")


@lru_cache(maxsize=1)
def engine():
    from kokoro_onnx import Kokoro
    return Kokoro(MODEL_PATH, VOICES_PATH)


def synthesize_wav(text: str, voice: str, speed: float = 1.0, language: str = "en-us") -> bytes:
    if not isinstance(text, str) or not text.strip() or len(text) > 4000:
        raise ValueError("input must be a non-empty string of at most 4000 characters")
    if not isinstance(voice, str) or not voice or len(voice) > 100 or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789_-" for c in voice):
        raise ValueError("invalid voice name")
    if not 0.5 <= speed <= 2.0:
        raise ValueError("speed must be between 0.5 and 2.0")

    if language in ("it", "it-it"):
        from misaki.espeak import EspeakG2P
        phonemes, _ = EspeakG2P(language="it")(text)
        if not phonemes:
            raise ValueError("Italian phonemization returned no phonemes")
        samples, rate = engine().create(phonemes, voice=voice, speed=speed, is_phonemes=True)
    elif language in ("en", "en-us", "en-gb"):
        samples, rate = engine().create(text, voice=voice, speed=speed, lang="en-gb" if language == "en-gb" else "en-us")
    else:
        raise ValueError("language must be en-us, en-gb, or it")

    pcm = (np.clip(np.asarray(samples), -1, 1) * 32767).astype("<i2")
    buf = io.BytesIO()
    with wave.open(buf, "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(int(rate))
        out.writeframes(pcm.tobytes())
    return buf.getvalue()
