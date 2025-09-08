import subprocess
import json
import firebase_admin
from firebase_admin import credentials, firestore
import argparse
import os
import sys
from backend.data.database import firestore_db 
from backend.scripts.normalize import normalize_file
from backend.data.schemas import CodingProblems



def upload_to_firestore(output_path: str):
    """Upload normalized JSON to Firebase Firestore."""
    
    with open(output_path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    problems = [CodingProblems(**item) for item in raw]
    firestore_db.set_coding_problems(problems)


def cleanup_file(files: list):
    """Delete a file if it exists."""
    for path in files:
        if os.path.exists(path):
            os.remove(path)
            print(f"Removed temporary file: {path}")
        else:
            print(f"No file found to remove: {path}")


def main():
    input_file = "backend/scripts/leetcode_problems.json"
    output_file = "backend/scripts/cleaned.json"
    first_n = 1000   # set an int if you want to limit, e.g. 10
    overrides = None # or path to overrides.json
    start_id = 1
    # normalize_file(input_file, output_file, first_n, start_id, overrides)
    # print(upload_to_firestore(output_file))
    cleanup_file([output_file, input_file])



if __name__ == "__main__":
    main()
