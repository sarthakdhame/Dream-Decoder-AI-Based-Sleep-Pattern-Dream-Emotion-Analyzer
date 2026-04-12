# Dream Decoder

Dream Decoder is a full-stack Flask + Vanilla JS application for dream journaling, multilingual NLP analysis, sleep tracking, analytics, and Jungian interpretation.

## Features

- Dream journal with sentiment, emotion, keywords, and interpretation
- Sleep log with quality metrics and dream correlation
- Jungian analysis powered by Gemini (with fallback behavior)
- Analytics dashboard with global time range filter:
	- 7, 14, 30, 60, 90, 180, 365 days
- Multilingual processing (English, Hindi, Marathi, Hinglish)
- JWT-based authentication

## Tech Stack

- Backend: Python, Flask, SQLite
- Frontend: HTML, CSS, Vanilla JavaScript, Chart.js
- NLP/AI: Transformers, spaCy, Gemini API
- Auth: PyJWT + bcrypt

## Project Structure

- `backend/` Flask APIs, services, models, DB logic
- `frontend/` static UI (HTML/CSS/JS)
- `data/` SQLite DB files
- `scripts/maintenance/` utility and maintenance scripts
- `tests/` test and validation scripts
- `app.py` root Flask entrypoint for deployment platforms (including Vercel)

## Local Setup (Windows)

1. Clone repository.
2. Create `.env` in project root (or update existing one).
3. Run `setup.bat`.
4. Run `start.bat`.
5. Open `http://localhost:5000`.

## Environment Variables

Common variables:

- `GEMINI_API_KEY` - required for Jungian AI analysis
- `PORT` - server port (default: `5000`)
- `HOST` - server host (default: `0.0.0.0`)
- `CORS_ORIGINS` - optional; comma-separated origins or `*` (default)

Example:

```env
GEMINI_API_KEY=your_key_here
PORT=5000
HOST=0.0.0.0
CORS_ORIGINS=*
```

## Deployment Notes

- `backend/app.py` is the canonical Flask app.
- Root `app.py` is a thin wrapper for platform runtime discovery (`gunicorn app:app`).
- Deployed backend URL: `https://dream-decoder-ai-based-sleep-pattern.onrender.com`
- Deployed frontend URL: `https://dream-decoder-ai-based-sleep-patter.vercel.app`
- Frontend API client uses same-origin on Render and this backend URL for non-Render hosts.
- Recommended Render backend settings:
	- Root Directory: repository root
	- Build Command: `pip install -r requirements.txt`
	- Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT`
- Do not commit real secrets.

## Maintenance Scripts

Root clutter has been reduced. Utility scripts are now under:

- `scripts/maintenance/`

Examples include model listing, path fixes, and verification helpers.

## Security Notes

- Keep `.env` private.
- Rotate API keys if exposed.
- Set `CORS_ORIGINS` to specific domains in production.

## Run Tests (Optional)

- Use scripts in `tests/` and `scripts/` based on your verification needs.

## License

Add your preferred license information here.
