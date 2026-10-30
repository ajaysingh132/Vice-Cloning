# GBSBFORYOU Voice Engine Backend

FastAPI backend prototype for the V2.1 mobile frontend.

## Model

This first implementation uses the official Chatterbox Multilingual V3 runtime and selects Hindi with `language_id="hi"`. The separate Hindi single-language checkpoint is listed by the model publisher, but its exact loading interface must be validated before switching to it.

Official references:
- https://github.com/resemble-ai/chatterbox
- https://huggingface.co/ResembleAI/chatterbox
- https://huggingface.co/ResembleAI/Chatterbox-Multilingual-hi

## Requirements

- Python 3.11
- Linux host
- NVIDIA GPU recommended for practical inference; CPU mode may be very slow.
- FFmpeg and libsndfile
- Confirm current model and dependency licenses before commercial deployment.

## Run locally

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export ALLOWED_ORIGINS="https://ajaysingh132.github.io"
uvicorn main:app --host 0.0.0.0 --port 8000
```

The first request downloads/loads model weights. This may require several GB of disk and GPU memory.

## API

### GET /health

Returns service readiness and whether the model has loaded.

### POST /api/voice-clone

Multipart form fields:
- `text`: required; up to 2,000 characters
- `language`: `hi` or `en`
- `speaker_wav`: required audio file; up to 30 MB

Successful response: `audio/wav`.

Example:

```bash
curl -X POST "http://localhost:8000/api/voice-clone" \
  -F "text=नमस्कार। यह मेरी आवाज़ का परीक्षण है।" \
  -F "language=hi" \
  -F "speaker_wav=@reference.wav" \
  --output test.wav
```

## Privacy and safety

- Only use a reference voice you own or have explicit permission to use.
- The reference file is written to a temporary file only for inference and removed in the request cleanup.
- No user API key is needed in the browser.
- Production deployment must use HTTPS, private logs, storage quotas, rate limiting, and a narrowly configured CORS origin.
- This prototype does not implement a persistent voice-profile library.
- Do not expose this API publicly until authentication and abuse controls are added.

## Known prototype limitations

- No authentication or per-user quotas yet.
- No persistent voice profiles.
- Speed control is not implemented server-side.
- The generated output temp file needs a scheduled cleanup policy on a long-running host.
- Runtime compatibility and Hindi quality must be tested on the target GPU host before connecting the public frontend.
