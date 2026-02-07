from flask import Blueprint
import time
from firebase import db

test_phase0_bp = Blueprint("test_phase0", __name__)

# TEST 3 — Firestore WRITE
@test_phase0_bp.route("/firestore/write")
def test_firestore_write():
    db.collection("test_phase0").add({
        "status": "ok",
        "timestamp": time.time()
    })
    return "WRITE_OK"


# TEST 4 — Firestore READ
@test_phase0_bp.route("/firestore/read")
def test_firestore_read():
    docs = db.collection("test_phase0").limit(1).stream()
    for doc in docs:
        return doc.to_dict()
    return {"message": "NO_DATA"}


# TEST 5 — Simulated ESP32 Payload
@test_phase0_bp.route("/inject")
def test_inject():
    db.collection("rover_raw").add({
        "rover_id": "SIM-001",
        "gps": {"lat": 19.07, "lng": 72.87},
        "ultrasonic": {"distance": 25},
        "timestamp": time.time()
    })
    return "INJECTED"
