import requests
import logging
from config import settings

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/embeddings"


def is_ollama_available() -> bool:
    """Legacy stub — always True since we use OpenRouter embeddings."""
    return True


def generate_embedding(text: str) -> list[float]:
    """Generate an embedding vector using OpenRouter / OpenAI text-embedding-3-small."""
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.EMBEDDING_MODEL,
        "input": text,
    }
    try:
        response = requests.post(OPENROUTER_URL, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            return data["data"][0]["embedding"]
        else:
            logger.warning(f"Embedding API error {response.status_code}: {response.text}. Using zero vector.")
            return [0.0] * 1536
    except requests.RequestException as e:
        logger.error(f"Embedding connection error: {e}")
        return [0.0] * 1536
