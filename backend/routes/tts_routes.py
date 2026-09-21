from flask import Blueprint, jsonify, request

from services.tts_service import list_voices, synthesize_speech, TTSServiceError
from services.translation_service import translate_text, TranslationError
from utils.validators import validate_tts_payload, ValidationError

tts_bp = Blueprint("tts", __name__)


@tts_bp.route("/api/tts", methods=["POST"])
def generate_speech():
    if not request.is_json:
        return jsonify({"success": False, "error": "Content-Type must be application/json."}), 400

    try:
        data = validate_tts_payload(request.get_json(silent=True))
    except ValidationError as exc:
        return jsonify({"success": False, "error": exc.message}), exc.status_code

    text_to_speak = data["text"]
    translated_text = None
    translation_warning = None

    # Optional: translate the input text into the selected language before
    # speaking it, so typing English while Hindi is selected actually
    # produces Hindi speech instead of English words read in a Hindi voice.
    # If translation fails (e.g. the translation service is unreachable),
    # we don't hard-fail the whole request -- we fall back to speaking the
    # original text and let the frontend know translation didn't happen.
    if data["translate"]:
        try:
            translated_text = translate_text(data["text"], data["language"])
            text_to_speak = translated_text
        except TranslationError as exc:
            translation_warning = (
                f"Translation was unavailable, so the original text was spoken instead: {exc.message}"
            )

    try:
        filename = synthesize_speech(
            text=text_to_speak,
            language_code=data["language"],
            voice_name=data["voice"],
        )
    except TTSServiceError as exc:
        return jsonify({"success": False, "error": exc.message}), exc.status_code

    response_body = {"success": True, "audio_url": f"/audio/{filename}"}
    if translated_text:
        response_body["translated_text"] = translated_text
    if translation_warning:
        response_body["warning"] = translation_warning

    return jsonify(response_body), 200


@tts_bp.route("/api/voices", methods=["GET"])
def get_voices():
    language_code = request.args.get("language")

    try:
        voices = list_voices(language_code=language_code)
    except TTSServiceError as exc:
        return jsonify({"success": False, "error": exc.message}), exc.status_code

    return jsonify({"success": True, "voices": voices}), 200


@tts_bp.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200
