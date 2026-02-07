from flask import Flask
from flask_cors import CORS
from routes.rover_data import rover_data_bp
from routes.test_phase0 import test_phase0_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(rover_data_bp, url_prefix="/api")
app.register_blueprint(test_phase0_bp, url_prefix="/test")

@app.route("/")
def home():
    return {"status": "Smart Rover Backend Running"}

if __name__ == "__main__":
    app.run(debug=True)
