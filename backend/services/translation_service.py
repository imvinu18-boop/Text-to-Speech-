"""
Optional translation layer used before speech synthesis.

Tries MyMemory first (a proper free translation API with generous limits),
and falls back to Google Translate (via deep-translator's GoogleTranslator)
if MyMemory doesn't support the language pair or fails. MyMemory is tried
first on purpose: Google's free/unofficial endpoint enforces a strict 5
requests/second limit and blocks fairly easily on shared networks, whereas
MyMemory is a proper API with a much more forgiving free quota.

Note: unlike Google, MyMemory does NOT support source="auto" -- it needs an
explicit source language code, or it returns an error string instead of
raising. We do a small script-based guess (Devanagari/Gujarati Unicode
ranges) to pick a source language before calling it.

No API key or billing account required for either. This is what lets a
user type English text, pick Hindi as the language, and hear it spoken in
Hindi -- TTS on its own only pronounces the text you give it, it never
translates.
"""
import re

from deep_translator import GoogleTranslator, MyMemoryTranslator


class TranslationError(Exception):
    """Raised when translation fails or the service is unreachable."""

    def __init__(self, message, status_code=503):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


# When a translation provider is overloaded, blocked, rate-limited, or
# given input it can't handle, it can return an error string instead of a
# proper exception. deep-translator sometimes doesn't catch this and just
# hands back that string as if it were a "translation". These fragments
# are how those error messages read -- if we see them, treat it as a
# failure instead of speaking garbage.
_ERROR_PAGE_MARKERS = (
    "that's an error",
    "there was an error",
    "that's all we know",
    "error 500",
    "error 400",
    "too many requests",
    "invalid source language",
    "invalid target language",
)

# MyMemory (unlike Google) requires locale-style codes (hi-IN, not hi).
# Map our simple gTTS-style codes to what MyMemory expects.
_MYMEMORY_LANGUAGE_MAP = {
    "en": "en-GB",
    "hi": "hi-IN",
    "gu": "gu-IN",
    "mr": "mr-IN",
    "es": "es-ES",
    "fr": "fr-FR",
    "de": "de-DE",
}

# Small in-memory cache so repeated identical translations (e.g. clicking
# "Generate" more than once for the same text/language while testing)
# don't hit the translation API again. Not shared across processes/workers,
# just a per-run convenience -- it's fine if it's lost on restart.
_CACHE_MAX_ENTRIES = 200
_translation_cache = {}

_GUJARATI_RANGE = re.compile(r"[\u0A80-\u0AFF]")
_DEVANAGARI_RANGE = re.compile(r"[\u0900-\u097F]")  # covers Hindi & Marathi


def _guess_source_language(text):
    """
    MyMemory needs an explicit source language (no 'auto'). This is a
    lightweight script-based guess, not real language detection: it's
    only meant to disambiguate the languages this app actually offers.
    """
    if _GUJARATI_RANGE.search(text):
        return "gu"
    if _DEVANAGARI_RANGE.search(text):
        return "hi"
    return "en"


def _mymemory_code(language_code):
    return _MYMEMORY_LANGUAGE_MAP.get(language_code, language_code)


def _looks_like_error_page(translated, original_text):
    lowered = translated.lower()
    if any(marker in lowered for marker in _ERROR_PAGE_MARKERS):
        return True
    if len(original_text) < 100 and len(translated) > len(original_text) * 8:
        return True
    return False


def _cache_put(key, value):
    if len(_translation_cache) >= _CACHE_MAX_ENTRIES:
        _translation_cache.pop(next(iter(_translation_cache)))
    _translation_cache[key] = value


def translate_text(text, target_language):
    """
    Translates `text` into `target_language` (e.g. 'hi', 'gu', 'mr').
    Tries MyMemory first (more generous free limits), then falls back to
    Google if MyMemory can't handle the language pair or fails. Returns
    the translated string. Raises TranslationError if neither provider
    returns usable text.
    """
    text = (text or "").strip()
    if not text:
        raise TranslationError("There is no text to translate.", 400)

    cache_key = (text, target_language)
    if cache_key in _translation_cache:
        return _translation_cache[cache_key]

    translated = None
    last_error = None
    guessed_source = _guess_source_language(text)

    # --- Attempt 1: MyMemory -------------------------------------------------
    try:
        source_code = _mymemory_code(guessed_source)
        target_code = _mymemory_code(target_language)
        result = MyMemoryTranslator(source=source_code, target=target_code).translate(text)
        if result and result.strip() and not _looks_like_error_page(result, text):
            translated = result.strip()
        else:
            last_error = "MyMemory returned an empty or invalid result."
    except Exception as exc:
        last_error = str(exc)

    # --- Attempt 2: Google (fallback) ----------------------------------------
    if translated is None:
        try:
            result = GoogleTranslator(source="auto", target=target_language).translate(text)
            message = (result or "").lower()
            if any(marker in message for marker in ("not supported", "invalid")):
                raise TranslationError(f"Translation failed: {result}", 400)
            if result and result.strip() and not _looks_like_error_page(result, text):
                translated = result.strip()
            else:
                last_error = f"{last_error}; Google also returned an empty or invalid result." if last_error else "Google returned an empty or invalid result."
        except TranslationError:
            raise
        except Exception as exc:
            message = str(exc).lower()
            if "not supported" in message or "invalid" in message:
                raise TranslationError(f"Translation failed: {exc}", 400)
            last_error = f"{last_error}; Google also failed: {exc}" if last_error else f"Google failed: {exc}"

    if not translated:
        raise TranslationError(
            f"Translation service is unavailable right now (both providers failed: {last_error}). "
            "Please wait a moment and try again.",
            503,
        )

    _cache_put(cache_key, translated)
    return translated