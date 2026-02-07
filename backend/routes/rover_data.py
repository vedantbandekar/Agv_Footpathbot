import json
from flask import Blueprint, request, jsonify
from services.data_service import (
    save_telemetry,
    get_latest_rover_data,
    get_recent_telemetry,
    validate_payload,
    get_rover_status
)

rover_data_bp = Blueprint("rover_data", __name__)

@rover_data_bp.route("/telemetry", methods=["POST"])
def receive_telemetry():
    # 1. Check if the request is Multipart (contains files) or just JSON
    if request.is_json:
        data = request.get_json()
        image_file = None
    else:
        # Handling the 'Multipart' request from your new upload button
        json_data = request.form.get("data")
        data = json.loads(json_data) if json_data else None
        image_file = request.files.get("image")

    if not data:
        return jsonify({"error": "No data payload provided"}), 400

    # 2. Validate the telemetry fields
    valid, msg = validate_payload(data)
    if not valid:
        return jsonify({"error": msg}), 400

    # 3. Save telemetry (and upload image to Cloudinary if image_file exists)
    save_telemetry(data, image_file)
    
    return jsonify({"status": "OK"})
    
@rover_data_bp.route("/rover/latest", methods=["GET"])
def latest_rover_data():
    data = get_latest_rover_data()
    if not data:
        return jsonify({"error": "No rover data"}), 404
    return jsonify(data)


@rover_data_bp.route("/rover/history", methods=["GET"])
def rover_history():
    return jsonify(get_recent_telemetry())


@rover_data_bp.route("/rover/status", methods=["GET"])
def rover_status():
    return jsonify({"status": get_rover_status()})
