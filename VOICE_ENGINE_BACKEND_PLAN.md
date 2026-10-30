# GBSBFORYOU Voice Engine — Backend Integration Plan

Status: implementation planning branch; no live backend is deployed yet.

## Why this branch does not implement XTTS-v2

The XTTS-v2 model weights are distributed under the Coqui Public Model License (CPML), which permits non-commercial use only. It restricts use of both the model and generated outputs where direct or indirect payment arises. GBSBFORYOU publishes and distributes books and may monetize media, so XTTS-v2 must not be used for monetized or revenue-generating production unless an appropriate license is confirmed in writing. The original licensor's commercial licensing route is reported unavailable. Keep XTTS-v2 only for personal/non-commercial evaluation after accepting its terms.

Sources:
- https://huggingface.co/coqui/XTTS-v2/blob/main/LICENSE.txt
- https://github.com/coqui-ai/TTS/discussions/4304
- https://docs.coqui.ai/en/dev/models/xtts.html

## Proposed production candidate

Evaluate Resemble AI Chatterbox Multilingual V3 for Hindi voice cloning:
- Official model card: https://huggingface.co/ResembleAI/chatterbox
- Official repository: https://github.com/resemble-ai/chatterbox
- The official model card declares MIT licensing and lists Hindi among 23 supported languages.
- A dedicated Hindi model is listed as ResembleAI/Chatterbox-Multilingual-hi.
- Generated audio includes a PerTh watermark; preserve this and disclose AI-generated speech where appropriate.
- Before production, verify the exact license metadata and terms for the selected Hindi checkpoint, its dependencies, and any model assets. Do not assume the parent model card automatically governs every separate checkpoint.

## Integration architecture

Mobile browser (GitHub Pages V2.1 frontend)
  -> HTTPS FastAPI backend
  -> provider adapter interface
  -> Chatterbox model runtime (GPU preferred)
  -> WAV response

The browser must never contain model weights, private API keys, or server credentials.

## Initial API contract

- GET /health — returns service and model readiness (does not claim model loaded unless it is).
- POST /api/voice-clone — multipart form:
  - text: Hindi/English text (required, max 2,000 chars for first test)
  - speaker_wav: user's authorized reference recording (required, max 30 MB)
  - language: hi or en (first milestone)
  - speed: optional numeric control, if supported by chosen runtime
- Response: audio/wav on success; JSON error with safe message on failure.
- CORS: allow only the deployed GBSBFORYOU frontend origin(s), not wildcard in production.
- Do not persist reference recordings by default. Temporary files must be deleted after inference. Persistent voice profiles require explicit opt-in, encryption, retention controls, and delete/export controls.

## Milestones

1. Confirm the Hindi Chatterbox checkpoint's license and runtime compatibility.
2. Implement a FastAPI adapter and health endpoint.
3. Connect V2.1 frontend to the agreed multipart API contract.
4. Run a test with Ajay's own reference recording and compare pronunciation, similarity, latency, and output quality.
5. Add encrypted, opt-in voice profile storage only after successful testing.
6. Integrate the same backend adapter into GBSBFORYOU AI Video Studio.

## Acceptance checks

- Hindi Devanagari input produces intelligible Hindi speech.
- Only an authorized reference recording can be used.
- Upload limits and clear errors are enforced.
- Audio is returned as WAV and plays on Android Chrome.
- No credentials are stored in frontend localStorage.
- No audio is retained server-side unless the user explicitly opts in.
- License and watermark notices are preserved.

## Important limitation

This document is a plan only. Creating this branch does not deploy a server, install model weights, or activate voice cloning. A GPU-capable host or compatible inference service is still required.
