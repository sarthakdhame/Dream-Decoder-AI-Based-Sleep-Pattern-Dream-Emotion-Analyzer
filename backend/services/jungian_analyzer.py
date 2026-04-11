"""
Dream Decoder - Jungian Analyzer
Service for specialized Jungian Psychology dream analysis using Google Gemini API
"""
import os
from dotenv import load_dotenv

# Try to import Gemini AI, but don't fail the whole app if it's missing
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False
    print("WARNING: google-generativeai not installed. Jungian analysis will be disabled.")

# Load environment variables
load_dotenv(override=True)

PLACEHOLDER_KEYS = {"your_gemini_api_key_here", "", None}
MODEL_CANDIDATES = ("gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro")


def _get_gemini_key():
    """Read the current Gemini API key from environment variables."""
    load_dotenv(override=True)
    return os.getenv("GEMINI_API_KEY")


def _configure_gemini(key):
    """Configure the Gemini client if the key is usable."""
    if HAS_GEMINI and key and key not in PLACEHOLDER_KEYS:
        genai.configure(api_key=key)
        return True
    return False


GEMINI_API_KEY = _get_gemini_key()
if not _configure_gemini(GEMINI_API_KEY):
    print("WARNING: GEMINI_API_KEY not found in environment variables.")

def analyze_jungian(dream_text):
    """
    Analyze dream text using Jungian Psychology via Google Gemini API.
    """
    if not HAS_GEMINI:
        return {
            "error": "Google Generative AI library is not installed. Please run setup.bat to install it."
        }

    global GEMINI_API_KEY
    GEMINI_API_KEY = _get_gemini_key()
    if not _configure_gemini(GEMINI_API_KEY):
        return {
            "error": "Gemini API key not configured. Add a valid GEMINI_API_KEY to .env and restart the server."
        }

    if not GEMINI_API_KEY or GEMINI_API_KEY in PLACEHOLDER_KEYS:
        return {
            "error": "Gemini API key not configured. Add a valid GEMINI_API_KEY to .env and restart the server."
        }
    
    if not dream_text or len(dream_text.strip()) < 10:
        return {
            "error": "Dream text is too short for meaningful analysis."
        }

    try:
        # Structured prompt as requested
        prompt = f"""Analyze the following dream using Jungian Psychology. 
Focus on:
- Archetypes (Shadow, Anima/Animus, Self, Persona)
- Symbols and their deeper unconscious meanings
- Collective unconscious references
- Emotional interpretation
- Personal growth insight

Dream:
{dream_text}

Return output in simple, clear language.

Title: Jungian Interpretation
Sections:
1. Symbols Meaning: [Your analysis here]
2. Archetypes Identified: [Your analysis here]
3. Emotional Insight: [Your analysis here]
4. Personal Growth Message: [Your analysis here]
"""

        last_error = None
        for model_name in MODEL_CANDIDATES:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)

                if not response.text:
                    return {"error": "Received empty response from Gemini API."}

                return {
                    "analysis": response.text,
                    "provider": f"Google Gemini ({model_name})"
                }
            except Exception as model_error:
                last_error = model_error
                error_text = str(model_error).lower()

                if any(token in error_text for token in ("429", "quota", "exhausted")):
                    raise

                if any(token in error_text for token in ("404", "not found", "permission denied", "403", "access denied", "model")):
                    continue

                raise

        if last_error is not None:
            raise last_error
        
    except Exception as e:
        error_msg = str(e).lower()
        if "429" in error_msg or "quota" in error_msg or "exhausted" in error_msg:
            print("WARNING: Gemini API Quota Exceeded. Using fallback analysis.")
            fallback_text = (
                "1. Symbols Meaning: Your dream contains rich symbolism, but our AI is currently at maximum capacity. "
                "Commonly, symbols represent aspects of your waking life that need attention.\n\n"
                "2. Archetypes Identified: The characters in your dream often reflect parts of your own psyche—such as the Shadow "
                "(hidden fears) or the Anima/Animus (inner feminine/masculine).\n\n"
                "3. Emotional Insight: Your feelings during the dream are the most accurate guide to its meaning. "
                "Consider what emotions were strongest and how they relate to your current life.\n\n"
                "4. Personal Growth Message: Every dream is an opportunity to integrate hidden parts of yourself. "
                "Reflect on the symbols and how they might guide your waking choices."
            )
            return {
                "analysis": fallback_text,
                "provider": "Fallback (API Quota Exceeded)"
            }

        if any(token in error_msg for token in ("403", "permission denied", "access denied", "api key not valid", "unauthorized")):
            return {
                "error": "Gemini API key is invalid or does not have access to the requested model. Try a valid Google AI Studio key and restart the server."
            }

        if any(token in error_msg for token in ("404", "not found", "model")):
            return {
                "error": f"Gemini model unavailable for this key. Tried: {', '.join(MODEL_CANDIDATES)}"
            }
            
        print(f"ERROR in Jungian Analysis: {str(e)}")
        return {
            "error": f"Failed to perform Jungian analysis: {str(e)}"
        }
