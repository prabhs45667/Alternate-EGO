import requests
import json
import re
import logging
from config import settings

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def is_ollama_available() -> bool:
    """Legacy stub — always returns True since we now use OpenRouter."""
    return True


def _openrouter_chat(messages: list, max_tokens: int = 512) -> str:
    """Call OpenRouter chat completions API."""
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://alternate-ego.app",
        "X-Title": "Alternate Ego",
    }
    payload = {
        "model": settings.OPENROUTER_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "top_p": 0.9,
    }
    try:
        response = requests.post(OPENROUTER_URL, json=payload, headers=headers, timeout=60)
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        else:
            logger.error(f"OpenRouter error {response.status_code}: {response.text}")
            return f"I'm having trouble connecting right now. Please try again."
    except requests.RequestException as e:
        logger.error(f"OpenRouter connection error: {e}")
        return "I'm offline at the moment. Please try again."


def generate_response(prompt, system_prompt: str = "") -> str:
    """Generate text response using OpenRouter (grok-4.1-fast).

    Args:
        prompt: Either a string or a list of message dicts
                [{"role": "system"/"user"/"assistant", "content": "..."}]
        system_prompt: System prompt (only used when prompt is a string)
    """
    if isinstance(prompt, list):
        return _openrouter_chat(prompt)

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": str(prompt)})
    return _openrouter_chat(messages)


def generate_response_with_mood(prompt) -> tuple:
    """Generate text response AND detect mood in a single LLM call.

    Returns:
        Tuple of (response_text, mood_string)
    """
    raw_response = generate_response(prompt)

    mood = "neutral"
    clean_response = raw_response

    mood_match = re.search(r'\[MOOD:\s*(\w+)\s*\]', raw_response)
    if mood_match:
        mood = mood_match.group(1).lower()
        clean_response = raw_response[:mood_match.start()].strip()
        valid_moods = {"neutral", "happy", "excited", "sad", "angry", "thoughtful"}
        if mood not in valid_moods:
            mood = "neutral"
    else:
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
