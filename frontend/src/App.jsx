import { useEffect, useState } from "react";
import TextInput from "./components/TextInput.jsx";
import LanguageSelector, { SUPPORTED_LANGUAGES } from "./components/LanguageSelector.jsx";
import VoiceSelector from "./components/VoiceSelector.jsx";
import GenerateButton from "./components/GenerateButton.jsx";
import AudioPlayer from "./components/AudioPlayer.jsx";
import DownloadButton from "./components/DownloadButton.jsx";
import ErrorMessage from "./components/ErrorMessage.jsx";
import { fetchVoices, generateSpeech } from "./api.js";

const MAX_TEXT_LENGTH = 5000;

export default function App() {
  const [text, setText] = useState("");
  const [language, setLanguage] = useState(SUPPORTED_LANGUAGES[0].code);
  const [voices, setVoices] = useState([]);
  const [voice, setVoice] = useState("");
  const [voicesLoading, setVoicesLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [audioUrl, setAudioUrl] = useState("");
  const [error, setError] = useState("");
  const [translateEnabled, setTranslateEnabled] = useState(false);
  const [translatedText, setTranslatedText] = useState("");
  const [warning, setWarning] = useState("");

  // Reload voices whenever the selected language changes
  useEffect(() => {
    let cancelled = false;
    setVoicesLoading(true);
    setError("");
    setAudioUrl("");

    fetchVoices(language)
      .then((fetchedVoices) => {
        if (cancelled) return;
        setVoices(fetchedVoices);
        setVoice(fetchedVoices[0]?.name || "");
      })
      .catch(() => {
        if (cancelled) return;
        setVoices([]);
        setVoice("");
        setError(
          "Could not load voices for this language. Check that the backend server is running."
        );
      })
      .finally(() => {
        if (!cancelled) setVoicesLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [language]);

  async function handleGenerate() {
    setError("");

    if (!text.trim()) {
      setError("Please enter some text before generating speech.");
      return;
    }
    if (text.length > MAX_TEXT_LENGTH) {
      setError(`Text is too long. Please stay under ${MAX_TEXT_LENGTH} characters.`);
      return;
    }
    if (!voice) {
      setError("Please select a voice.");
      return;
    }

    setGenerating(true);
    setAudioUrl("");
    setTranslatedText("");
    setWarning("");
    try {
      const { url, translatedText: newTranslatedText, warning: newWarning } = await generateSpeech({
        text,
        language,
        voice,
        translate: translateEnabled,
      });
      setAudioUrl(url);
      if (newTranslatedText) setTranslatedText(newTranslatedText);
      if (newWarning) setWarning(newWarning);
    } catch (err) {
      const backendMessage = err?.response?.data?.error;
      if (err?.code === "ECONNABORTED" || err?.message === "Network Error") {
        setError("Network error: could not reach the backend server.");
      } else {
        setError(backendMessage || "Something went wrong while generating speech.");
      }
    } finally {
      setGenerating(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 flex items-start justify-center py-10 px-4">
      <div className="w-full max-w-xl bg-white rounded-2xl shadow-sm border border-slate-200 p-6 sm:p-8 space-y-6">
        <header>
          <h1 className="text-2xl font-semibold text-slate-900">Text to Speech</h1>
          <p className="text-sm text-slate-500 mt-1">
            Convert written text into natural-sounding speech.
          </p>
        </header>

        <TextInput value={text} onChange={setText} maxLength={MAX_TEXT_LENGTH} />

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <LanguageSelector value={language} onChange={setLanguage} />
          <VoiceSelector
            voices={voices}
            value={voice}
            onChange={setVoice}
            loading={voicesLoading}
          />
        </div>

        <label className="flex items-start gap-2 text-sm text-slate-600 cursor-pointer">
          <input
            type="checkbox"
            checked={translateEnabled}
            onChange={(e) => setTranslateEnabled(e.target.checked)}
            className="mt-0.5 h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-300"
          />
          <span>
            Translate my text into the selected language before speaking
            <span className="block text-xs text-slate-400">
              Turn this on if you typed in one language (e.g. English) but selected a
              different speaking language (e.g. Hindi).
            </span>
          </span>
        </label>

        <ErrorMessage message={error} />

        <GenerateButton
          onClick={handleGenerate}
          loading={generating}
          disabled={voicesLoading || !voice}
        />

        {audioUrl && (
          <div className="space-y-3 pt-2 border-t border-slate-100">
            {warning && (
              <div className="rounded-lg bg-amber-50 border border-amber-200 px-4 py-3 text-sm text-amber-800">
                {warning}
              </div>
            )}
            {translatedText && (
              <div className="rounded-lg bg-indigo-50 border border-indigo-100 px-4 py-3 text-sm text-indigo-800">
                <span className="font-medium">Spoken text: </span>
                {translatedText}
              </div>
            )}
            <AudioPlayer audioUrl={audioUrl} />
            <DownloadButton audioUrl={audioUrl} />
          </div>
        )}
      </div>
    </div>
  );
}
