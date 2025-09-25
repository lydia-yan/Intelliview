# Speech-to-Text with Vosk
We use **Vosk** for speech-to-text conversion in the backend.
This allows us to transcribe PCM audio (audio/pcm) into text in real-time or batch mode without relying on cloud APIs (no token cost)

## Setup
1. Install Python dependencies (from `requirements.txt`):
```bash
pip install -r requirements.txt
```
2. Download the **Vosk model** (not stored in GitHub because it’s large):
Run the provided script:
```bash
bash scripts/download_vosk_model.sh
```
This will:
- Download the English small model (`vosk-model-small-en-us-0.15`)
- Extract it into the `models/` folder
- Skip download if it’s already present

## Relevant files for speech to text
```
backend/
├── agents/
│   └── interviewer/
│       └── agent.py         # Main agent code handling audio/text messages
├── utils/
│   └── speech_to_text.py    # Wrapper for Vosk transcription
├── scripts/
│   └── download_vosk_model.sh   # Script to fetch/unzip Vosk model
├── requirements.txt
└── ...

```

## Deployment Notes (Google Cloud Run)
1. Model Handling
- The model is not stored in GitHub.
- We fetch it during the Docker build step via scripts/download_vosk_model.sh.
2. Add Dockerfile snippet