def extract_gps(payload: dict):
    gps = payload.get("gps", {})
    return {
        "lat": gps.get("lat"),
        "lng": gps.get("lng")
    }