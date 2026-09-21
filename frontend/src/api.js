import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";

const client = axios.create({
  baseURL: API_URL,
  timeout: 20000,
});

/**
 * Fetches available voices, optionally filtered by language code.
 */
export async function fetchVoices(languageCode) {
  const response = await client.get("/api/voices", {
    params: languageCode ? { language: languageCode } : {},
  });
  return response.data.voices;
}

/**
 * Sends text + voice config to the backend and returns the audio URL.
 * When `translate` is true, the backend translates the text into the
 * selected language before speaking it; the translated text (if any) is
 * returned alongside the audio URL so the UI can show what was spoken.
 */
export async function generateSpeech({ text, language, voice, translate }) {
  const response = await client.post("/api/tts", { text, language, voice, translate });
  const audioPath = response.data.audio_url;
  return {
    url: `${API_URL}${audioPath}`,
    translatedText: response.data.translated_text || null,
    warning: response.data.warning || null,
  };
}

export { API_URL };
