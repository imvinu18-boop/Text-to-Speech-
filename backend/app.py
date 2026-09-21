import os

from dotenv import load_dotenv
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

load_dotenv()

from routes.tts_routes import tts_bp  # noqa: E402  (import after load_dotenv)
from services.tts_service import AUDIO_DIR  # noqa: E402

app = Flask(__name__)

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
CORS(app, resources={r"/api/*": {"origins": FRONTEND_ORIGIN}, r"/audio/*": {"origins": FRONTEND_ORIGIN}})

limiter = Limiter(get_remote_address, app=app, default_limits=["60 per minute"])
limiter.limit("10 per minute")(tts_bp)

app.register_blueprint(tts_bp)


@app.route("/audio/<path:filename>", methods=["GET"])
def serve_audio(filename):
    return send_from_directory(AUDIO_DIR, filename)


@app.errorhandler(404)
def not_found(_error):
    return jsonify({"success": False, "error": "Resource not found."}), 404


@app.errorhandler(429)
def rate_limited(_error):
    return jsonify({"success": False, "error": "Too many requests. Please slow down."}), 429


@app.errorhandler(500)
def server_error(_error):
    return jsonify({"success": False, "error": "Internal server error."}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
