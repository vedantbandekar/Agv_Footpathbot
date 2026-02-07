import requests
import time
import random

URL = "http://127.0.0.1:5000/api/rover/data"

payload = {
    "rover_id": "SR-001",
    "timestamp": int(time.time()),
    "gps": {"lat": 19.0760, "lng": 72.8777},
    "ultrasonic": {"distance_cm": random.uniform(10, 60)},
    "hazard": {
        "detected": True,
        "type": "pothole",
        "severity": "high",
        "probability": 0.78
    },
    "status": {"speed": 1.1, "sos": False}
}

requests.post(URL, json=payload)
