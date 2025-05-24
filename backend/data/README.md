# Firestore Database Setup Guide

### 1. Download the Firebase Key  
- Download the `firebase-key.json` from the shared [Google Drive link](https://drive.google.com/drive/folders/1zJE616rPCja9FTuYRf2He_sUTzVAJQ0i?usp=sharing).

### 2. Save the Key  
- Create the `credentials` folder under the `backend/` directory
- Place the file inside: `backend/credentials/firebase-key.json`

### 3. Add the Environment Variable
In the `backend/.env` file, add the following line:
```ini
FIREBASE_KEY_PATH=credentials/firebase-key.json
```

### 4.Install Dependencies
- (Optional) Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```
- Install required packages:
```bash
pip install -r backend/requirements.txt
```

## Run the Tests
From the `backend` directory, run:
```bash
pytest ./data/tests/test_db.py -v
```
> The `-v` flag stands for verbose mode.
> It shows each test name and whether it passed, failed, or errored.