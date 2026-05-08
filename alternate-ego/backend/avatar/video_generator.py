"""Video Avatar Generation — SadTalker lip-sync pipeline.

SadTalker generates a talking-head video from a still face image + audio.
This module handles the integration workflow:
  1. Get reference face image (neutral emotion photo)
  2. Get reference audio (latest TTS output)
  3. Run SadTalker to produce a lip-synced MP4
  4. Serve the video at /static/storage/videos/{twin_id}/

SadTalker Setup (one-time, manual):
  git clone https://github.com/OpenTalker/SadTalker
  cd SadTalker
  pip install -r requirements.txt
  # Download checkpoints:
  bash scripts/download_models.sh  (Linux/Mac)
  # OR manually from: https://github.com/OpenTalker/SadTalker#download-trained-models

Wav2Lip Alternative (faster but lower quality):
  git clone https://github.com/Rudrabha/Wav2Lip
  pip install -r requirements.txt
  # Download wav2lip.pth from https://github.com/Rudrabha/Wav2Lip#getting-the-weights
"""

import os
import uuid
import logging
import subprocess
import shutil
import sys
from typing import Optional
from config import settings

logger = logging.getLogger(__name__)

# ─── Config ───────────────────────────────────────────────
SADTALKER_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "SadTalker"))
WAV2LIP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "Wav2Lip"))
VIDEOS_DIR = os.path.join(settings.STORAGE_DIR, "videos")


def _build_subprocess_env() -> dict:
    """Build an environment for video tools with ffmpeg available when packaged."""
    env = os.environ.copy()

    try:
        import imageio_ffmpeg

        ffmpeg_dir = os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe())
        env["PATH"] = ffmpeg_dir + os.pathsep + env.get("PATH", "")
    except Exception:
        pass

    return env


def is_sadtalker_available() -> bool:
    """Check if SadTalker is installed and checkpoints exist."""
    inference_script = os.path.join(SADTALKER_DIR, "inference.py")
    checkpoints = os.path.join(SADTALKER_DIR, "checkpoints")
    return os.path.exists(inference_script) and os.path.exists(checkpoints)


def is_wav2lip_available() -> bool:
    """Check if Wav2Lip is installed and weights exist."""
    inference_script = os.path.join(WAV2LIP_DIR, "inference.py")
    weights = os.path.join(WAV2LIP_DIR, "checkpoints", "wav2lip.pth")
    return os.path.exists(inference_script) and os.path.exists(weights)


def generate_video_sadtalker(image_path: str, audio_path: str, output_path: str) -> bool:
    """Run SadTalker to generate a lip-synced video.

    Args:
        image_path: Path to source face image (JPEG/PNG)
        audio_path: Path to driving audio (WAV/MP3)
        output_path: Path where the output MP4 should be saved

    Returns:
        True on success, False on failure
    """
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)

    cmd = [
        sys.executable, os.path.join(SADTALKER_DIR, "inference.py"),
        "--driven_audio", audio_path,
        "--source_image", image_path,
        "--result_dir", output_dir,
        "--still",                      # Use still mode for portrait photos
        "--preprocess", "full",         # Process full image (not just face crop)
        "--enhancer", "gfpgan",         # Enhance face quality with GFPGAN
    ]

    try:
        logger.info(f"Running SadTalker: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,               # 5 minutes max
            cwd=SADTALKER_DIR,
            env=_build_subprocess_env(),
        )

        if result.returncode != 0:
            logger.error(f"SadTalker failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}")
            return False

        # SadTalker saves to result_dir with a generated name — find the mp4
        mp4_files = [f for f in os.listdir(output_dir) if f.endswith(".mp4")]
        if not mp4_files:
            logger.error("SadTalker completed but no MP4 found in output dir.")
            return False

        # Move to our expected output_path
        generated = os.path.join(output_dir, mp4_files[-1])
        if generated != output_path:
            shutil.move(generated, output_path)

        logger.info(f"✅ SadTalker video generated: {output_path}")
        return True

    except subprocess.TimeoutExpired:
        logger.error("SadTalker timed out after 5 minutes.")
        return False
    except Exception as e:
        logger.error(f"SadTalker error: {e}")
        return False


def generate_video_wav2lip(image_path: str, audio_path: str, output_path: str) -> bool:
    """Run Wav2Lip to generate a lip-synced video (faster alternative).

    Args:
        image_path: Path to source face image or video
        audio_path: Path to driving audio
        output_path: Path where output MP4 will be saved

    Returns:
        True on success, False on failure
    """
    weights_path = os.path.join(WAV2LIP_DIR, "checkpoints", "wav2lip.pth")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    cmd = [
        sys.executable, os.path.join(WAV2LIP_DIR, "inference.py"),
        "--checkpoint_path", weights_path,
        "--face", image_path,
        "--audio", audio_path,
        "--outfile", output_path,
        "--nosmooth",
    ]

    try:
        logger.info(f"Running Wav2Lip: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            cwd=WAV2LIP_DIR,
            env=_build_subprocess_env(),
        )

        if result.returncode != 0:
            logger.error(f"Wav2Lip failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}")
            return False

        if os.path.exists(output_path):
            logger.info(f"✅ Wav2Lip video generated: {output_path}")
            return True

        logger.error("Wav2Lip completed but output file not found.")
        return False

    except subprocess.TimeoutExpired:
        logger.error("Wav2Lip timed out.")
        return False
    except Exception as e:
        logger.error(f"Wav2Lip error: {e}")
        return False


def generate_talking_avatar(twin_id: str, audio_path: str) -> Optional[str]:
    """Main function — generate a lip-synced video for a twin.

    Tries SadTalker first (better quality), then falls back to Wav2Lip.
    The face image is taken from the neutral emotion photo captured during onboarding.

    Args:
        twin_id: The twin's UUID
        audio_path: Path to the TTS audio to drive the lip sync

    Returns:
        Path to the generated video file, or None on failure
    """
    # Prefer the generated avatar files from the current onboarding flow.
    image_candidates = [
        os.path.join(settings.AVATARS_DIR, twin_id, "neutral_avatar.png"),
        os.path.join(settings.AVATARS_DIR, twin_id, "happy_avatar.png"),
        os.path.join(settings.AVATARS_DIR, twin_id, "sad_avatar.png"),
        os.path.join(settings.AVATARS_DIR, twin_id, "angry_avatar.png"),
        os.path.join(settings.AVATARS_DIR, twin_id, "original.jpg"),
        os.path.join(settings.AVATARS_DIR, twin_id, "neutral.jpg"),
    ]
    image_path = next((path for path in image_candidates if os.path.exists(path)), "")
    if not image_path:
        logger.warning(f"No avatar image found for twin {twin_id}. Cannot generate video.")
        return None

    if not os.path.exists(audio_path):
        logger.warning(f"Audio file not found: {audio_path}")
        return None

    image_path = os.path.abspath(image_path)
    audio_path = os.path.abspath(audio_path)

    # Prepare output path
    videos_dir = os.path.abspath(os.path.join(VIDEOS_DIR, twin_id))
    os.makedirs(videos_dir, exist_ok=True)
    video_id = uuid.uuid4().hex[:8]
    output_path = os.path.join(videos_dir, f"avatar_{video_id}.mp4")

    # Try SadTalker first
    if is_sadtalker_available():
        logger.info("Using SadTalker for video generation.")
        success = generate_video_sadtalker(image_path, audio_path, output_path)
        if success and os.path.exists(output_path):
            return output_path

    # Fallback to Wav2Lip
    if is_wav2lip_available():
        logger.info("Using Wav2Lip for video generation (SadTalker unavailable).")
        success = generate_video_wav2lip(image_path, audio_path, output_path)
        if success and os.path.exists(output_path):
            return output_path

    logger.warning(
        "Neither SadTalker nor Wav2Lip is available. "
        "Set up SadTalker: git clone https://github.com/OpenTalker/SadTalker "
        "OR Wav2Lip: git clone https://github.com/Rudrabha/Wav2Lip"
    )
    return None


def get_latest_video(twin_id: str) -> Optional[str]:
    """Get the most recently generated video for a twin."""
    videos_dir = os.path.join(VIDEOS_DIR, twin_id)
    if not os.path.exists(videos_dir):
        return None

    mp4_files = sorted(
        [f for f in os.listdir(videos_dir) if f.endswith(".mp4")],
        key=lambda f: os.path.getmtime(os.path.join(videos_dir, f)),
        reverse=True
    )

    if mp4_files:
        return os.path.join(videos_dir, mp4_files[0])
    return None


def delete_videos(twin_id: str):
    """Delete all generated videos for a twin."""
    videos_dir = os.path.join(VIDEOS_DIR, twin_id)
    if os.path.exists(videos_dir):
        shutil.rmtree(videos_dir)
        logger.info(f"🗑️ Deleted videos for twin {twin_id}")
