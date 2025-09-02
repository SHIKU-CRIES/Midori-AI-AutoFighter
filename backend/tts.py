from __future__ import annotations

import io
from typing import Optional

try:  # pragma: no cover - optional dependency
    from chatterbox_tts import ChatterboxTTS
except Exception:  # pragma: no cover
    try:  # pragma: no cover
        from chatterbox import ChatterboxTTS  # type: ignore
    except Exception:  # pragma: no cover
        ChatterboxTTS = None  # type: ignore

_model: ChatterboxTTS | None = None


def _load_model() -> Optional[ChatterboxTTS]:
    global _model
    if _model is None and ChatterboxTTS is not None:
        try:
            _model = ChatterboxTTS.from_pretrained()
        except Exception:
            _model = None
    return _model


def generate_voice(text: str, audio_prompt_path: str | None = None) -> Optional[bytes]:
    model = _load_model()
    if model is None:
        return None
    try:
        audio = model.generate(text, audio_prompt_path=audio_prompt_path)
    except Exception:
        return None
    if isinstance(audio, bytes):
        return audio
    try:
        buffer = io.BytesIO()
        audio.export(buffer, format="wav")  # type: ignore[attr-defined]
        return buffer.getvalue()
    except Exception:
        return None
