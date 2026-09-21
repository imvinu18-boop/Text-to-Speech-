"""
Request validation helpers for the /api/tts endpoint.
Keeping validation in one place makes it easy to test and reuse.
"""
import os

MAX_TEXT_LENGTH = int(os.getenv("MAX_TEXT_LENGTH", 5000))


class ValidationError(Exception):
    """Raised when incoming request data fails validation."""

    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def validate_tts_payload(data):
    """
    Validates the JSON body sent to POST /api/tts.
    Expected shape: { "text": str, "language": str, "voice": str }
    Raises ValidationError on any problem.
    """
    if not data:
        raise ValidationError("Request body must be valid JSON.", 400)

    text = data.get("text", "")
    language = data.get("language", "")
    voice = data.get("voice", "")
    translate = data.get("translate", False)

    if not isinstance(text, str) or not text.strip():
        raise ValidationError("Field 'text' is required and cannot be empty.", 400)

    if len(text) > MAX_TEXT_LENGTH:
        raise ValidationError(
            f"Field 'text' exceeds the maximum length of {MAX_TEXT_LENGTH} characters.",
            400,
        )

    if not isinstance(language, str) or not language.strip():
        raise ValidationError("Field 'language' is required.", 400)

    if not isinstance(voice, str) or not voice.strip():
        raise ValidationError("Field 'voice' is required.", 400)

    if not isinstance(translate, bool):
        raise ValidationError("Field 'translate' must be true or false.", 400)

    return {
        "text": text.strip(),
        "language": language.strip(),
        "voice": voice.strip(),
        "translate": translate,
    }
