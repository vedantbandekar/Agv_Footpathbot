from firebase import db
import time
import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv
import uuid

load_dotenv() # This loads the variables from the .env file

cloudinary.config( 
  cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"), 
  api_key = os.getenv("CLOUDINARY_API_KEY"), 
  api_secret = os.getenv("CLOUDINARY_API_SECRET"),
  secure = True
)
COLLECTION = "rover_telemetry"

REQUIRED_FIELDS = ["rover_id", "gps", "ultrasonic"]

def validate_payload(payload: dict):
    for field in REQUIRED_FIELDS:
        if field not in payload:
            return False, f"Missing field: {field}"

    gps = payload.get("gps", {})
    if "lat" not in gps or "lng" not in gps:
        return False, "Invalid GPS structure"

    ultra = payload.get("ultrasonic", {})
    if "distance" not in ultra:
        return False, "Invalid ultrasonic structure"

    return True, "OK"

def save_telemetry(payload: dict, image_file=None):
    payload["server_timestamp"] = time.time()
    
    # If an image was sent, upload it first and add the link to the data
    if image_file:
        payload["image_url"] = upload_image_and_get_url(image_file)
        
    db.collection(COLLECTION).add(payload)
    return True

def get_latest_rover_data():
    # Order by timestamp descending to get the newest one
    docs = db.collection(COLLECTION).order_by("server_timestamp", direction="DESCENDING").limit(1).stream()
    for doc in docs:
        return doc.to_dict()
    return None

def get_recent_telemetry(limit=5):
    docs = (
        db.collection(COLLECTION)
        .order_by("server_timestamp", direction="DESCENDING")
        .limit(limit)
        .stream()
    )
    return [doc.to_dict() for doc in docs]

def get_rover_status(timeout_sec=5):
    data = get_latest_rover_data()
    if not data:
        return "OFFLINE"

    last = data.get("server_timestamp", 0)
    return "ONLINE" if time.time() - last <= timeout_sec else "OFFLINE"

def upload_image_and_get_url(file_obj):
    """Uploads a file to Cloudinary and returns the secure URL."""
    try:
        # Create a unique public ID so images don't overwrite each other
        unique_id = f"rover_capture_{int(time.time())}_{uuid.uuid4().hex[:6]}"
        
        upload_result = cloudinary.uploader.upload(
            file_obj, 
            public_id = unique_id,
            folder = "rover_missions"
        )
        
        # Return the secure HTTPS URL
        return upload_result.get("secure_url")
    except Exception as e:
        print(f"Cloudinary Upload Failed: {e}")
        return None