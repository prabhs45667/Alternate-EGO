import requests
import json
import re
import logging
from config import settings

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://127.0.0.1:11434/api"

def is_ollama_available() -> bool:
    """Check if Ollama local server is running."""
    try:
        response = requests.get("http://127.0.0.1:11434/", timeout=2)
        return response.status_code == 200
    except requests.RequestException:
        return False

def generate_response(prompt, system_prompt: str = "") -> str:
    """Generate text response using Ollama.
    
    Args:
        prompt: Either a string (simple prompt) or a list of message dicts
                [{"role": "system"/"user"/"assistant", "content": "..."}]
        system_prompt: System prompt (only used when prompt is a string)
    """
    try:
        # If prompt is a list of messages, use /api/chat (multi-turn)
        if isinstance(prompt, list):
            response = requests.post(
                f"{OLLAMA_URL}/chat",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "messages": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": 256,
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "repeat_penalty": 1.1,
                    }
                },
                timeout=45
            )
            if response.status_code == 200:
                return response.json().get("message", {}).get("content", "")
            else:
                logger.error(f"Ollama chat error HTTP {response.status_code}: {response.text}")
                return f"Error: Ollama returned status {response.status_code}"
        
        # If prompt is a string, use /api/generate (simple)
        response = requests.post(
            f"{OLLAMA_URL}/generate",
            json={
                "model": settings.OLLAMA_MODEL,
                "prompt": str(prompt),
                "system": system_prompt,
                "stream": False,
                "options": {
                    "num_predict": 256,
                    "temperature": 0.7,
                    "top_p": 0.9,
                }
            },
            timeout=45
        )
        if response.status_code == 200:
            return response.json().get("response", "")
        else:
            logger.error(f"Ollama generation error HTTP {response.status_code}: {response.text}")
            return f"Error: Ollama returned status {response.status_code}"
    except requests.RequestException as e:
        logger.error(f"Ollama generation connection error: {e}")
        return f"Error connecting to Ollama: {str(e)}"


def generate_response_with_mood(prompt) -> tuple:
    """Generate text response AND detect mood in a single LLM call.
    
    The system prompt instructs the model to end with [MOOD:xxx].
    This function parses it out, saving a full separate LLM call.
    
    Returns:
        Tuple of (response_text, mood_string)
    """
    raw_response = generate_response(prompt)
    
    # Parse mood tag from response
    mood = "neutral"
    clean_response = raw_response
    
    mood_match = re.search(r'\[MOOD:\s*(\w+)\s*\]', raw_response)
    if mood_match:
        mood = mood_match.group(1).lower()
        clean_response = raw_response[:mood_match.start()].strip()
        # Validate mood
        valid_moods = {"neutral", "happy", "excited", "sad", "angry", "thoughtful"}
        if mood not in valid_moods:
            mood = "neutral"
    else:
        # Fallback: quick keyword-based mood detection (no LLM call needed)
        mood = _detect_mood_fast(raw_response)
    
    return clean_response, mood


def _detect_mood_fast(text: str) -> str:
    """Ultra-fast keyword-based mood detection — no LLM call needed."""
    text_lower = text.lower()
    
    happy_words = {"happy", "glad", "excited", "love", "great", "awesome", "wonderful", 
                   "amazing", "fantastic", "joy", "delighted", "thrilled", "haha", "lol",
                   "😊", "😄", "😁", "🎉", "❤️", "proud", "grateful", "blessed"}
    sad_words = {"sad", "miss", "sorry", "unfortunately", "regret", "difficult", "hard",
                 "tough", "struggle", "pain", "😢", "😞", "heartbreak", "lost"}
    angry_words = {"angry", "frustrated", "annoyed", "hate", "terrible", "awful", 
                   "ridiculous", "unacceptable", "😠", "furious", "mad"}
    thoughtful_words = {"think", "consider", "reflect", "perhaps", "maybe", "interesting",
                        "hmm", "wonder", "perspective", "🤔", "ponder", "believe", "actually"}
    excited_words = {"excited", "can't wait", "thrilled", "pumped", "stoked", "🤩",
                     "incredible", "mind-blowing", "breakthrough"}
    
    # Count matches
    scores = {
        "happy": sum(1 for w in happy_words if w in text_lower),
        "sad": sum(1 for w in sad_words if w in text_lower),
        "angry": sum(1 for w in angry_words if w in text_lower),
        "thoughtful": sum(1 for w in thoughtful_words if w in text_lower),
        "excited": sum(1 for w in excited_words if w in text_lower),
    }
    
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "neutral"


def detect_mood(message: str) -> str:
    """Fast mood detection — uses keywords, NOT a separate LLM call."""
    return _detect_mood_fast(message)
