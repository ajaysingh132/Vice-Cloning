---
title: GBSBFORYOU Hindi Voice Clone
emoji: 🎙️
colorFrom: yellow
colorTo: purple
sdk: gradio
sdk_version: 5.49.1
app_file: app.py
pinned: false
---

# GBSBFORYOU Hindi Voice Clone — ZeroGPU Test

This folder is intended to be uploaded as the root of a new Hugging Face Space.

## Create the Space

1. Sign in to Hugging Face.
2. Create a new Space named `gbsbforyou-hindi-voice`.
3. Choose **Gradio** SDK.
4. Choose **Public** only if you are comfortable with the demo being publicly accessible. For private recordings, prefer a private Space if your account supports it.
5. Upload `app.py`, `requirements.txt`, and this README at the Space root.
6. In Space Settings, select **ZeroGPU** hardware if your account is eligible.
7. Wait for the Space to build, then inspect the Logs.

## Important ZeroGPU constraints

- ZeroGPU Spaces use Gradio and GPU decorators; this app is a Gradio test endpoint, not the FastAPI server.
- Free personal accounts must meet Hugging Face eligibility requirements; current documentation says verified email and account age over 30 days, up to two ZeroGPU Spaces.
- The free tier has a limited daily GPU quota. It is suitable for short tests, not continuous production service.
- The app requests up to 120 seconds of GPU execution per generation.
- The first run downloads model weights and may take time.

## Model

Uses `ChatterboxMultilingualTTS.from_pretrained(device, t3_model="v3")` and `model.generate(..., language_id="hi", audio_prompt_path=...)`.

The model publisher lists a Hindi fine-tune at `ResembleAI/Chatterbox-Multilingual-hi`; this demo currently uses the official multilingual runtime with Hindi language selection. A later test should compare the Hindi fine-tune and the V3 multilingual checkpoint.

## Privacy

- Do not publish another person's voice without explicit permission.
- This demo does not save a named voice profile.
- Uploaded audio is used for generation only by the Space runtime; review the platform's current data/privacy terms before uploading sensitive recordings.
- Do not treat this public demo as a production service. Add authentication, rate limits, access controls and retention controls before wider use.
