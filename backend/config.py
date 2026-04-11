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
_cors_origins_raw = os.environ.get('CORS_ORIGINS', '').strip()
if _cors_origins_raw:
    # If CORS_ORIGINS env var is set, use it
    if _cors_origins_raw == '*':
        CORS_ORIGINS = '*'
    else:
        CORS_ORIGINS = [origin.strip() for origin in _cors_origins_raw.split(',') if origin.strip()]
else:
    # Default production origins
    CORS_ORIGINS = [
        'https://dreamdecoder.vercel.app',
        'https://dream-decoder-701m.onrender.com',
        'http://localhost:3000',
        'http://127.0.0.1:3000'
    ]

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
