import pytest, os
from backend.tools.transcript_utils import transcribe_audio_bytes

def test_transcribe_known_audio_sample():
    # Load a sample audio file (you can use your own short WAV file with known content)
    current_dir = os.path.dirname(__file__)
    sample_path = os.path.join(current_dir, "samples", "hello_world.wav")
    with open(sample_path, "rb") as f:
        audio_bytes = f.read()

    result = transcribe_audio_bytes(audio_bytes)
    print(result)

    assert isinstance(result, str)
    assert len(result) > 0
    assert "hello" in result.lower()  # Expected keyword
