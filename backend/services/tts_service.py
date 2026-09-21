"""
Wraps the gTTS (Google Text-to-Speech) library.

gTTS is a free, unofficial wrapper around Google Translate's speech engine.
No API key or billing account is required. Trade-offs versus Google Cloud
TTS:
  - No distinct male/female "voices" -- only accent variants via the
    Google Translate domain (tld), which we model as "voices" below.
  - No SSML / pitch / speaking-rate controls.
  - It depends on an unofficial endpoint, so it can be rate-limited or
    change without notice -- fine for learning/small projects, not for
    guaranteed production SLAs.
"""
import os
import uuid

from gtts import gTTS
from gtts.tts import gTTSError

AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "generated_audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

# gTTS has no real "voice" concept -- each language only has accent
# variants (via tld). We expose those variants as "voices" so the rest
# of the app (routes, frontend) doesn't need to change shape.
VOICE_OPTIONS = {
    "en": [
        {"name": "en-us", "tld": "com", "label": "US English"},
        {"name": "en-uk", "tld": "co.uk", "label": "UK English"},
        {"name": "en-in", "tld": "co.in", "label": "Indian English"},
        {"name": "en-au", "tld": "com.au", "label": "Australian English"},
    ],
    "hi": [{"name": "hi-in", "tld": "co.in", "label": "Hindi (India)"}],
    "gu": [{"name": "gu-in", "tld": "co.in", "label": "Gujarati (India)"}],
    "mr": [{"name": "mr-in", "tld": "co.in", "label": "Marathi (India)"}],
    "es": [
        {"name": "es-es", "tld": "es", "label": "Spanish (Spain)"},
        {"name": "es-mx", "tld": "com.mx", "label": "Spanish (Mexico)"},
    ],
    "fr": [
        {"name": "fr-fr", "tld": "fr", "label": "French (France)"},
        {"name": "fr-ca", "tld": "ca", "label": "French (Canada)"},
    ],
    "de": [{"name": "de-de", "tld": "de", "label": "German"}],
}

SUPPORTED_LANGUAGES = list(VOICE_OPTIONS.keys())


class TTSServiceError(Exception):
    """Raised when gTTS fails, is unreachable, or gets bad input."""

    def __init__(self, message, status_code=503):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def list_voices(language_code=None):
    """
    Returns the available "voices" (accent variants), optionally
    filtered by language code (e.g. 'en', 'hi').
    """
    if language_code:
        if language_code not in VOICE_OPTIONS:
            raise TTSServiceError(f"Language '{language_code}' is not supported.", 400)
        return VOICE_OPTIONS[language_code]

    all_voices = []
    for voices in VOICE_OPTIONS.values():
        all_voices.extend(voices)
    return all_voices


def _find_voice(language_code, voice_name):
    for voice in VOICE_OPTIONS.get(language_code, []):
        if voice["name"] == voice_name:
            return voice
    return None


def synthesize_speech(text, language_code, voice_name, audio_format="MP3"):
    """
    Sends text to gTTS and writes the resulting MP3 to generated_audio/.
    Returns the filename (not the full path) so the caller can build a
    public URL. gTTS only supports MP3 output, so audio_format is ignored
    beyond validation.
    """
    if language_code not in VOICE_OPTIONS:
        raise TTSServiceError(f"Language '{language_code}' is not supported.", 400)

    voice = _find_voice(language_code, voice_name)
    if voice is None:
        raise TTSServiceError(
            f"Voice '{voice_name}' is not valid for language '{language_code}'.", 400
        )

    try:
        tts = gTTS(text=text, lang=language_code, tld=voice["tld"])
    except (ValueError, AssertionError) as exc:
        raise TTSServiceError(f"Invalid text or language for TTS: {exc}", 400)

    filename = f"{uuid.uuid4().hex}.mp3"
    filepath = os.path.join(AUDIO_DIR, filename)

    try:
        tts.save(filepath)
    except gTTSError as exc:
        raise TTSServiceError(f"gTTS service is unavailable right now: {exc}", 503)
    except Exception as exc:
        raise TTSServiceError(f"Failed to generate speech: {exc}", 500)

    return filename
