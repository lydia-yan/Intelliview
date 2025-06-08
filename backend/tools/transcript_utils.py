import whisper
import tempfile

# Load Whisper once globally
model = whisper.load_model("small")  # use "tiny" or "small" if running on CPU only

def transcribe_audio_bytes(audio_bytes: bytes) -> str:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
        tmp.write(audio_bytes)
        tmp.flush()
        result = model.transcribe(tmp.name)
        return result["text"].strip() if result["text"] else "[unrecognized audio]"
