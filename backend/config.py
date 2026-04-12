"""
Dream Decoder - Configuration Settings
"""
import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database
DATABASE_PATH = os.path.join(BASE_DIR, '..', 'data', 'dream_decoder.db')

# Flask settings
DEBUG = True
HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', 5000))

# CORS settings
_default_cors_origins = [
    'https://dreamdecoder.vercel.app',
    'https://dreamdecoder-chi.vercel.app',
    'https://dream-decoder-ai-based-sleep-patter.vercel.app',
    'https://dream-decoder-7fy3.onrender.com',
    'https://dream-decoder-701m.onrender.com',
    # Allow future Render frontend URLs for this project pattern.
    r'https://dream-decoder-.*\.onrender\.com',
    'http://localhost:3000',
    'http://127.0.0.1:3000'
]

_cors_origins_raw = os.environ.get('CORS_ORIGINS', '').strip()
if _cors_origins_raw == '*':
    CORS_ORIGINS = '*'
elif _cors_origins_raw:
    # Merge env-defined origins with defaults so stale env vars do not break deployments.
    _env_origins = [origin.strip() for origin in _cors_origins_raw.split(',') if origin.strip()]
    CORS_ORIGINS = list(dict.fromkeys(_env_origins + _default_cors_origins))
else:
    CORS_ORIGINS = _default_cors_origins

# NLP Model settings
EMOTION_MODEL = 'AnasAlokla/multilingual_go_emotions'
SENTIMENT_MODEL = 'lxyuan/distilbert-base-multilingual-cased-sentiments-student'
SPACY_MODEL = 'en_core_web_sm'

# Common dream themes/keywords to detect
DREAM_THEMES = [
    'falling', 'flying', 'chased', 'chasing', 'running', 'trapped',
    'lost', 'naked', 'teeth', 'water', 'drowning', 'death', 'dying',
    'school', 'exam', 'test', 'late', 'missing', 'found', 'searching',
    'monster', 'ghost', 'dark', 'light', 'flying', 'floating',
    'car', 'driving', 'crash', 'accident', 'falling', 'heights',
    'house', 'home', 'room', 'door', 'stairs', 'elevator',
    'family', 'friend', 'stranger', 'baby', 'child', 'animal'
]
