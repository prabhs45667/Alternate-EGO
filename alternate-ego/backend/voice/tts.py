"""Text-to-Speech — ElevenLabs API for high-quality speech synthesis."""
import os
import logging
import uuid
import requests
from config import settings

logger = logging.getLogger(__name__)

ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1/text-to-speech"


def generate_speech_elevenlabs(text: str, output_path: str, voice_id: str = None) -> str:
    """Generate speech using ElevenLabs API.

    Args:
        text: Text to synthesize
        output_path: Path to save the .mp3 file
        voice_id: ElevenLabs voice ID (defaults to settings)

    Returns:
        Path to generated audio file, or empty string on failure
    """
    voice_id = voice_id or settings.ELEVENLABS_VOICE_ID
    url = f"{ELEVENLABS_API_URL}/{voice_id}"
    headers = {
        "xi-api-key": settings.ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    payload = {
        "text": text,
        "model_id": "eleven_turbo_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
        },
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(response.content)
            logger.info(f"✅ ElevenLabs TTS generated: {output_path}")
            return output_path
        else:
            logger.error(f"❌ ElevenLabs error {response.status_code}: {response.text}")
            return ""
    except Exception as e:
        logger.error(f"❌ ElevenLabs TTS failed: {e}")
        return ""


def generate_speech(text: str, twin_id: str, output_dir: str = None) -> str:
    """Main TTS function — uses ElevenLabs for synthesis.

    Returns:
        Path to generated audio file
    """
    if not text or len(text.strip()) < 2:
        return ""

    if not output_dir:
        output_dir = os.path.join(settings.AUDIO_DIR, twin_id)
    os.makedirs(output_dir, exist_ok=True)

    filename = f"tts_{uuid.uuid4().hex[:8]}.mp3"
    output_path = os.path.join(output_dir, filename)

    # Truncate long text to keep TTS fast and cost-effective
    tts_text = text[:500] if len(text) > 500 else text

    return generate_speech_elevenlabs(tts_text, output_path)

