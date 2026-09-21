import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL;

const client = axios.create({
  baseURL: API_URL,
  timeout: 20000,
});

export async function fetchVoices(languageCode) {
  const response = await client.get("/api/voices", {
    params: languageCode ? { language: languageCode } : {},
  });
  return response.data.voices;
}

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
