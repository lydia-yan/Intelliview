import json
import numpy as np
from vosk import Model, KaldiRecognizer

# Load Vosk model once (update the path if you put the model elsewhere)
# Make sure you've unzipped vosk-model-small-en-us-0.15
vosk_model = Model("models/vosk-model-small-en-us-0.15")

def run_speech_to_text(pcm_bytes: bytes, sample_rate: int = 16000) -> str:
    """
    Convert raw PCM16 audio bytes into text using Vosk.

    Args:
        pcm_bytes (bytes): PCM16 little-endian audio data.
        sample_rate (int): Sample rate of the audio (default 16kHz).

    Returns:
        str: Transcribed text or fallback if transcription fails.
    """
    try:
        # Convert raw PCM bytes → numpy int16 array
        audio_array = np.frombuffer(pcm_bytes, dtype=np.int16)

        # Create recognizer
        recognizer = KaldiRecognizer(vosk_model, sample_rate)

        # Feed audio into recognizer
        recognizer.AcceptWaveform(audio_array.tobytes())
        result = json.loads(recognizer.FinalResult())

        return result.get("text", "").strip() or "[untranscribed audio]"
    except Exception as e:
        print(f"[ERROR] Vosk transcription failed: {e}")
        return "[untranscribed audio]"
