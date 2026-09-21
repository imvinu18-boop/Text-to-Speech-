# Text-to-Speech Application (Level 1 — Basic)

React + Flask + **gTTS** (free, no API key, no billing account).

## Features
- Enter/paste text with live character & word count
- Select language and voice/accent
- Optional "translate before speaking" toggle — type in English, select
  Hindi (or any supported language), and it translates then speaks it in
  that language (uses free `deep-translator`, no API key)
- Generate speech (completely free — no Google Cloud account needed)
- Play audio in-browser
- Download generated audio
- Validation and error handling (empty text, over-limit text, invalid voice/language, network/API failures)

## Important: TTS does not translate on its own
Selecting a language only tells the engine *how to pronounce* the text you
give it — it does not translate your words. If you type English text with
Hindi selected, you'll hear English words read oddly, not real Hindi. Turn
on the "Translate my text" toggle in the UI (or send `"translate": true`
to `/api/tts`) to have the backend translate your text into the selected
language first.

## Why gTTS instead of Google Cloud TTS?
Google Cloud TTS requires a billing account (card on file) even to use its
free monthly quota. **gTTS** is a free, unofficial library that uses Google
Translate's speech engine — no signup, no key, no card, ever.

Trade-offs to know about:
- No true male/female voices — only accent variants (US/UK/Indian English, etc.)
- No SSML, pitch, or speaking-rate controls
- It's an unofficial wrapper around a public endpoint, so heavy use can get
  rate-limited by Google. Fine for learning projects and small apps — not
  guaranteed for production-scale traffic.

## Project Structure
```
text-to-speech/
├── backend/       Flask API + gTTS integration
└── frontend/      React (Vite) + Tailwind CSS UI
```

## Prerequisites
- Python 3.9+
- Node.js 18+
- Internet connection (gTTS calls Google Translate's endpoint under the hood)

## Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Nothing to fill in for gTTS -- defaults work out of the box.

python app.py
```
The API runs at `http://localhost:5000`.

Verify it's up:
```bash
curl http://localhost:5000/api/health
```

## Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env   # defaults to http://localhost:5000, edit if needed
npm run dev
```
Open `http://localhost:5173`.

## API Reference

### `POST /api/tts`
```json
{
  "text": "My name is Vinod",
  "language": "hi",
  "voice": "hi-in",
  "translate": true
}
```
Response (when `translate` is true, `translated_text` is included so the UI
can show what was actually spoken):
```json
{
  "success": true,
  "audio_url": "/audio/generated-file.mp3",
  "translated_text": "मेरा नाम विनोद है"
}
```
`translate` is optional and defaults to `false` — leave it off (or omit it)
when your text is already in the selected language's script.

### `GET /api/voices?language=en`
Returns available voice/accent variants for the given language.

### `GET /api/health`
```json
{ "status": "ok" }
```

## Status Codes
| Code | Meaning |
|------|---------|
| 200  | Success |
| 400  | Invalid request (empty text, over limit, bad language/voice, bad Content-Type) |
| 404  | Resource not found |
| 429  | Rate limit exceeded (10 requests/min on `/api/tts`) |
| 500  | Internal server error |
| 503  | gTTS endpoint unavailable |

## Security Notes
- `.env` is git-ignored — no secrets needed here, but keep the habit for future providers.
- CORS is restricted to `FRONTEND_ORIGIN`.
- `/api/tts` is rate-limited to reduce the chance of Google rate-limiting your server's IP.
- Text length is capped server-side (`MAX_TEXT_LENGTH`), not just in the UI.

## Next Steps (Level 2/3)
See the original project spec for optional features: user auth, speech history,
favorites, PDF/DOCX upload, AI text enhancement, and cloud audio storage.
If you later need real male/female voices or SSML control without billing,
consider `edge-tts` (Microsoft Edge's free online voices) as a drop-in
replacement for `services/tts_service.py`.
