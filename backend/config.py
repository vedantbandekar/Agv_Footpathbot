import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FIREBASE_KEY_PATH = os.path.join(
    BASE_DIR, "..", "firebase", "serviceAccountKey.json"
)

DEBUG = True
