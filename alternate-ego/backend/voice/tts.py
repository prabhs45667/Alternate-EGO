"""Text-to-Speech fallback chain for chat replies and talking-avatar audio.

Priority:
1. Coqui XTTS v2 voice cloning when available
2. Edge-TTS
3. gTTS
4. pyttsx3
"""
import asyncio
import logging
import os
import threading
import uuid

from config import settings

logger = logging.getLogger(__name__)

_tts_model = None
_tts_model_loaded = False


def _get_tts_model():
    """Load and cache the optional Coqui XTTS model."""
    global _tts_model, _tts_model_loaded

    if _tts_model_loaded:
        return _tts_model

    _tts_model_loaded = True

    if not settings.USE_COQUI:
        logger.info("Coqui XTTS is disabled in settings")
        return None

    try:
        from TTS.api import TTS

        logger.info("Loading Coqui XTTS v2 model")
        _tts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
        logger.info("Coqui XTTS v2 model loaded")
        return _tts_model
    except ImportError:
        logger.warning("Coqui TTS package is not installed; falling back to Edge-TTS")
        return None
    except Exception as exc:
        logger.error("Failed to load Coqui XTTS model: %s", exc)
        return None


async def generate_speech_edge(text: str, output_path: str, voice: str = None) -> str:
    """Generate speech with Microsoft Edge TTS."""
    try:
        import edge_tts

        selected_voice = voice or settings.EDGE_TTS_VOICE
        communicate = edge_tts.Communicate(text, selected_voice)
        await communicate.save(output_path)

        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            logger.info("Edge-TTS generated: %s", output_path)
            return output_path
        return ""
    except Exception as exc:
        logger.error("Edge-TTS failed: %s", exc)
        return ""


def generate_speech_sync(text: str, output_path: str, voice: str = None) -> str:
    """Run Edge-TTS from synchronous call sites."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return _generate_speech_sync_internal(text, output_path, voice)

    result_holder = {"path": ""}

    def _worker() -> None:
        result_holder["path"] = _generate_speech_sync_internal(text, output_path, voice)

    worker = threading.Thread(target=_worker, daemon=True)
    worker.start()
    worker.join()
    return result_holder["path"]


def _generate_speech_sync_internal(text: str, output_path: str, voice: str = None) -> str:
    """Run Edge-TTS in a dedicated event loop."""
    loop = None
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(generate_speech_edge(text, output_path, voice))
    except Exception as exc:
        logger.error("Edge-TTS sync wrapper failed: %s", exc)
        return ""
    finally:
        if loop is not None:
            loop.close()
        asyncio.set_event_loop(None)


def generate_speech_gtts(text: str, output_path: str) -> str:
    """Generate speech with Google TTS."""
    try:
        from gtts import gTTS

        tts = gTTS(text=text, lang="en", slow=False)
        tts.save(output_path)

        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            logger.info("gTTS generated: %s", output_path)
            return output_path
        return ""
    except ImportError:
        logger.warning("gTTS is not installed")
        return ""
    except Exception as exc:
        logger.error("gTTS failed: %s", exc)
        return ""


def generate_speech_pyttsx3(text: str, output_path: str) -> str:
    """Generate speech with the local OS voice as a last resort."""
    try:
        import pyttsx3

        wav_path = output_path.replace(".mp3", ".wav")
        engine = pyttsx3.init()
        engine.setProperty("rate", 150)
        engine.setProperty("volume", 0.9)
        engine.save_to_file(text, wav_path)
        engine.runAndWait()

        if os.path.exists(wav_path) and os.path.getsize(wav_path) > 0:
            try:
                from pydub import AudioSegment

                audio = AudioSegment.from_wav(wav_path)
                audio.export(output_path, format="mp3", bitrate="128k")
                os.remove(wav_path)
                logger.info("pyttsx3 generated: %s", output_path)
                return output_path
            except Exception:
                logger.info("pyttsx3 generated WAV output: %s", wav_path)
                return wav_path
        return ""
    except ImportError:
        logger.warning("pyttsx3 is not installed")
        return ""
    except Exception as exc:
        logger.error("pyttsx3 failed: %s", exc)
        return ""


def generate_speech_xtts(text: str, twin_id: str, output_path: str) -> str:
    """Generate speech with Coqui XTTS using the user's voice reference."""
    tts = _get_tts_model()
    if tts is None:
        return ""

    ref_path = os.path.join(settings.VOICES_DIR, twin_id, "reference.wav")
    if not os.path.exists(ref_path):
        logger.warning("No reference voice found for twin %s; creating one", twin_id)
        try:
            from voice.voice_manager import create_voice_reference

            ref_path = create_voice_reference(twin_id)
            if not ref_path or not os.path.exists(ref_path):
                logger.warning("Could not create a voice reference for twin %s", twin_id)
                return ""
        except Exception as exc:
            logger.warning("Voice reference creation failed: %s", exc)
            return ""

    try:
        wav_output = output_path.replace(".mp3", ".wav")
        tts.tts_to_file(
            text=text,
            speaker_wav=ref_path,
            language="en",
            file_path=wav_output,
        )

        try:
            from pydub import AudioSegment

            audio = AudioSegment.from_wav(wav_output)
            audio.export(output_path, format="mp3", bitrate="128k")
            os.remove(wav_output)
            logger.info("XTTS voice clone generated: %s", output_path)
            return output_path
        except Exception:
            logger.info("XTTS voice clone generated WAV output: %s", wav_output)
            return wav_output
    except Exception as exc:
        logger.error("XTTS voice cloning failed: %s", exc)
        return ""


def generate_speech(text: str, twin_id: str, output_dir: str = None) -> str:
    """Generate speech using the fallback chain."""
    if not text or len(text.strip()) < 2:
        return ""

    if not output_dir:
        output_dir = os.path.join(settings.AUDIO_DIR, twin_id)
    os.makedirs(output_dir, exist_ok=True)

    filename = f"tts_{uuid.uuid4().hex[:8]}.mp3"
    output_path = os.path.join(output_dir, filename)
    tts_text = text[:500] if len(text) > 500 else text

    if settings.USE_COQUI:
        result = generate_speech_xtts(tts_text, twin_id, output_path)
        if result:
            return result
        logger.info("XTTS unavailable; falling back to Edge-TTS")

    result = generate_speech_sync(tts_text, output_path)
    if result:
        return result

    logger.info("Edge-TTS unavailable; falling back to gTTS")
    result = generate_speech_gtts(tts_text, output_path)
    if result:
        return result

    logger.info("gTTS unavailable; falling back to pyttsx3")
    result = generate_speech_pyttsx3(tts_text, output_path)
    if result:
        return result

    logger.warning("All TTS backends failed; no audio was generated")
    return ""

