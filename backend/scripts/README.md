# Data Cleaning & Firestore Upload (One-off Script)

This script normalizes a raw LeetCode problems JSON and (optionally) uploads the cleaned data to Firebase Firestore. It’s meant to be a **one-time utility**, not part of the running app.

## Before You Start

1. Download the original [data file](https://www.kaggle.com/datasets/alishohadaee/leetcode-problems-dataset?select=leetcode_problems.json) from Kaggle.  
2. Place it in the `script` directory.  
3. Make sure the file is named `leetcode_problems.json`.  

## What it does

1. Normalize input JSON → write to `cleaned.json`.
2. Upload `cleaned.json` to Firestore (via `firestore_db.set_coding_problems`).
3. **Cleanup** temporary files (`cleaned.json`, the input file) when done.

> In the current snippet, `normalize_file(...)` and `upload_to_firestore(...)` are commented out. Uncomment the lines you need.

## Repo layout (relevant paths)
```
backend/
- data/
-- database.py # Firestore client init (used by firestore_db)
-- schemas.py # Pydantic model: CodingProblems
- scripts/
-- run_clean_and_upload.py # <— this script
-- leetcode_problems.json # input (raw)
-- cleaned.json # output (generated)
-- normalize.py # normalization logic (imported by the script)
```

## Prerequisites
- **Python 3.9+**
- Dependencies (install in your venv):

## Configure (edit the script)
Open backend/scripts/run_clean_and_upload.py and set these:
```python
input_file = "backend/scripts/leetcode_problems.json"
output_file = "backend/scripts/cleaned.json"
first_n = 1000     # limit number of items (e.g., 10). Use None for all.
overrides = None   # or "backend/scripts/overrides.json"
start_id = 1       # starting ID for normalized items
```

Uncomment what you want to run:
```python
# normalize_file(input_file, output_file, first_n, start_id, overrides)
# print(upload_to_firestore(output_file))
cleanup_file([output_file, input_file])
```
- Only normalize: uncomment normalize_file(...).
- Only upload: make sure cleaned.json exists, then uncomment upload_to_firestore(...).
- Both: uncomment both lines.
- Cleanup: cleanup_file(...) will remove the listed files at the end. Keep or remove as you prefer.

## Run
From the repo root:
```bash
python3 -m backend.scripts.run_and_upload
```

## Safety tips
- Dry run first:
  - Run with only `normalize_file(...)` uncommented to produce cleaned.json using **`first_n = 5`** .
  - Inspect `cleaned.json` manually.
- **Note:** The `leetcode_problems.json` and `cleaned.json` file has already been added to `.gitignore`, so it won’t be pushed to GitHub.  