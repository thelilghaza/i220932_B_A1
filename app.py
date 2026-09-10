import os
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_version():
    version_file = os.path.join(os.path.dirname(__file__), "VERSION")
    if os.path.exists(version_file):
        with open(version_file, "r") as f:
            return f.read().strip()
    return "1.0.0"

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "application": "student-ml-api",
        "application_version": get_version(),
        "model_version": "model-1"
    }), 200

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid or missing JSON payload"}), 400

    if "value" not in data:
        return jsonify({"error": "Missing input: 'value' field is required"}), 400

    val = data["value"]
    if isinstance(val, bool) or not isinstance(val, (int, float)):
        return jsonify({"error": "Invalid input: 'value' must be a numeric value"}), 400

    prediction = val * 2
    return jsonify({
        "input": val,
        "prediction": prediction
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
