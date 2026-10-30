import os
import tempfile
import threading
from pathlib import Path

import gradio as gr
import spaces
import torch
import torchaudio
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

MODEL = None
MODEL_LOCK = threading.Lock()
GEN_LOCK = threading.Lock()
MAX_TEXT = 1200
MAX_AUDIO_BYTES = 25 * 1024 * 1024


def get_model():
    global MODEL
    if MODEL is None:
        with MODEL_LOCK:
            if MODEL is None:
                device = "cuda" if torch.cuda.is_available() else "cpu"
                # Official Chatterbox multilingual V3 model loading interface.
                MODEL = ChatterboxMultilingualTTS.from_pretrained(
                    device,
                    t3_model=os.getenv("CHATTERBOX_MULTILINGUAL_T3_MODEL", "v3"),
                )
    return MODEL


@spaces.GPU(duration=120)
def generate_voice(text, language, reference_audio):
    if not text or not text.strip():
        raise gr.Error("कृपया बोलने के लिए टेक्स्ट लिखें।")
    if len(text) > MAX_TEXT:
        raise gr.Error(f"पहले परीक्षण में अधिकतम {MAX_TEXT} अक्षर लिखें।")
    if not reference_audio:
        raise gr.Error("अपनी आवाज़ की reference recording अपलोड करें।")
    if not os.path.isfile(reference_audio):
        raise gr.Error("अपलोड की गई ऑडियो फाइल उपलब्ध नहीं है।")
    if os.path.getsize(reference_audio) > MAX_AUDIO_BYTES:
        raise gr.Error("Reference audio 25 MB से छोटी रखें।")
    if language not in ("hi", "en"):
        raise gr.Error("इस परीक्षण में केवल हिंदी और English उपलब्ध हैं।")

    output_path = None
    try:
        with GEN_LOCK:
            model = get_model()
            wav = model.generate(
                text.strip(),
                language_id=language,
                audio_prompt_path=reference_audio,
            )
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as out:
                output_path = out.name
            torchaudio.save(output_path, wav.detach().cpu(), model.sr)
        return output_path
    except gr.Error:
        raise
    except Exception as exc:
        print(f"Voice generation error: {type(exc).__name__}: {exc}")
        raise gr.Error("ऑडियो नहीं बन पाया। Space Logs में तकनीकी त्रुटि देखें।")


with gr.Blocks(title="GBSBFORYOU Voice Engine") as demo:
    gr.Markdown(
        """
        # 🎙️ GBSBFORYOU — Hindi Voice Clone Test
        **Chatterbox Multilingual V3 · ZeroGPU prototype**

        केवल अपनी आवाज़ या अनुमति-प्राप्त रिकॉर्डिंग का उपयोग करें।
        पहले छोटे वाक्य से गुणवत्ता जाँचें।
        """
    )
    with gr.Row():
        language = gr.Dropdown(
            choices=[("हिन्दी", "hi"), ("English", "en")],
            value="hi",
            label="भाषा",
        )
    text = gr.Textbox(
        label="बोलने के लिए टेक्स्ट",
        lines=5,
        max_lines=10,
        max_length=MAX_TEXT,
        placeholder="नमस्कार। यह मेरी आवाज़ का परीक्षण है।",
    )
    reference = gr.Audio(
        label="अपनी reference voice recording",
        type="filepath",
        sources=["upload", "microphone"],
    )
    consent = gr.Checkbox(
        label="मैं पुष्टि करता हूँ कि यह मेरी अपनी आवाज़ है या मुझे इसका उपयोग करने की अनुमति है।",
        value=False,
    )
    generate = gr.Button("🎧 मेरी आवाज़ में ऑडियो बनाएँ", variant="primary")
    output = gr.Audio(label="Generated WAV", type="filepath")
    note = gr.Markdown(
        "यह prototype है। Voice recording को स्थायी profile के रूप में सहेजने की सुविधा नहीं है।"
    )

    def guarded_generate(text_value, language_value, reference_value, consent_value):
        if not consent_value:
            raise gr.Error("पहले आवाज़ के स्वामित्व/अनुमति की पुष्टि करें।")
        return generate_voice(text_value, language_value, reference_value)

    generate.click(
        guarded_generate,
        inputs=[text, language, reference, consent],
        outputs=output,
    )

demo.queue(max_size=8).launch()
