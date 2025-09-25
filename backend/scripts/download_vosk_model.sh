#!/bin/bash
MODEL_URL="https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
MODEL_DIR="models/vosk-model-small-en-us-0.15"

if [ ! -d "$MODEL_DIR" ]; then
  echo "Downloading Vosk model..."
  mkdir -p models
  curl -L -o models/vosk-model-small-en-us-0.15.zip $MODEL_URL
  unzip models/vosk-model-small-en-us-0.15.zip -d models
else
  echo "Model already exists, skipping download."
fi
