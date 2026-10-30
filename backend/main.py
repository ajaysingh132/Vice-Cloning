import os
import tempfile
import threading
from pathlib import Path
from typing import Optional

import torch
import torchaudio
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

APP_VERSION = "0.1.0"
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", str(30 * 1024 * 1024)))
MAX_TEXT_CHARS = int(os.getenv("MAX_TEXT_CHARS", "2000"))
ALLOWED_LANGUAGES = {"hi", "en"}
ALLOWED_AUDIO_TYPES = {
    "audio/wav", "audio/x-wav", "audio/mpeg", "audio/mp3",
    "audio/mp4", "audio/m4a", "audio/aac", "audio/ogg",
    "audio/webm", "application/octet-stream",
}
ALLOWED_ORIGINS = [
    item.strip()
    for item in os.getenv("ALLOWED_ORIGINS", "https://ajaysingh132.github.io").split(",")
    if item.strip()
]

app = FastAPI(
    title="GBSBFORYOU Voice Engine API",
    version=APP_VERSION,
    description="Private, non-persistent Hindi voice cloning API using Chatterbox Multilingual.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

_model = None
_model_lock = threading.Lock()
_generation_lock = threading.Lock()
_model_error: Optional[str] = None


def get_model():
    global _model, _model_error
    if _model is not None:
        return _model
    with _model_lock:
        if _model is not None:
            return _model
        try:
            device = "cuda" if torch.cuda.is_available() else (
                "mps" if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available() else "cpu"
            )
            # The official Chatterbox multilingual V3 API exposes Hindi via language_id="hi".
            _model = ChatterboxMultilingualTTS.from_pretrained(
                device=device,
                t3_model="v3",
            )
            _model_error = None
            return _model
        except Exception as exc:
            _model_error = f"{type(exc).__name__}: {exc}"
            raise


@app.get("/")
def root():
    return {
        "service": "GBSBFORYOU Voice Engine",
        "version": APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "gbsbforyou-voice-engine",
        "version": APP_VERSION,
        "model_loaded": _model is not None,
        "model_error": _model_error,
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "languages": sorted(ALLOWED_LANGUAGES),
    }


@app.post("/api/voice-clone")
async def voice_clone(
    text: str = Form(...),
    language: str = Form("hi"),
    speaker_wav: UploadFile = File(...),
):
    text = text.strip()
    language = language.strip().lower()

    if not text:
        raise HTTPException(status_code=400, detail="Text is required.")
    if len(text) > MAX_TEXT_CHARS:
        raise HTTPException(status_code=413, detail=f"Text exceeds {MAX_TEXT_CHARS} characters.")
    if language not in ALLOWED_LANGUAGES:
        raise HTTPException(status_code=400, detail="Supported languages for this milestone: hi, en.")
    if speaker_wav.content_type and speaker_wav.content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(status_code=415, detail="Upload an audio recording (WAV, MP3, M4A, AAC, OGG or WebM).")

    suffix = Path(speaker_wav.filename or "reference.wav").suffix.lower()
    if suffix not in {".wav", ".mp3", ".m4a", ".aac", ".ogg", ".webm", ".mp4"}:
        suffix = ".wav"

    reference_path = None
    output_path = None
    try:
        raw = await speaker_wav.read()
        if not raw:
            raise HTTPException(status_code=400, detail="The reference audio file is empty.")
        if len(raw) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="Reference audio exceeds the 30 MB upload limit.")

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as ref_file:
            ref_file.write(raw)
            reference_path = ref_file.name

        # Serialize inference because one model instance is shared by requests.
        with _generation_lock:
            model = get_model()
            wav = model.generate(
                text,
                language_id=language,
                audio_prompt_path=reference_path,
            )
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as out_file:
                output_path = out_file.name
            torchaudio.save(output_path, wav.detach().cpu(), model.sr)

        return FileResponse(
            output_path,
            media_type="audio/wav",
            filename="gbsbforyou-voice-output.wav",
            background=None,
        )
    except HTTPException:
        raise
    except Exception as exc:
        # Do not expose stack traces, filesystem paths, or model internals to clients.
        raise HTTPException(
            status_code=503,
            detail=f"Voice generation failed ({type(exc).__name__}). Check backend logs.",
        )
    finally:
        if reference_path and os.path.exists(reference_path):
            os.remove(reference_path)
        # Output is returned as a temporary file. A later cleanup worker/container
        # lifecycle removes it; no voice profile or reference recording is persisted.
        await speaker_wav.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
