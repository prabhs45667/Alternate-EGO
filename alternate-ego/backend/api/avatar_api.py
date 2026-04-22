"""Avatar API — video generation + photo serving endpoints."""
import os
import uuid
import logging
from fastapi import APIRouter
from pydantic import BaseModel
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


class VideoRequest(BaseModel):
    twin_id: str
    text: str  # Text that was spoken (used to find/create audio)


@router.post("/generate-video")
async def generate_video_avatar(req: VideoRequest):
    """Generate a lip-synced talking-head video for the last TTS audio.

    Flow:
      1. Find the most recently generated TTS audio for this twin
      2. Find the neutral face photo from onboarding
      3. Run SadTalker or Wav2Lip
      4. Return the video URL
    """
    from avatar.video_generator import generate_talking_avatar, get_latest_video
    from voice.tts import generate_speech

    twin_id = req.twin_id

    try:
        # Step 1: Generate TTS audio for the text
        logger.info(f"Generating TTS audio for video: {req.text[:60]}...")
        audio_path = generate_speech(req.text[:300], twin_id)

        if not audio_path:
            return {
                "status": "error",
                "message": "Could not generate TTS audio. Check that Edge-TTS or Coqui XTTS is working.",
                "video_url": ""
            }

        # Step 2: Generate video
        logger.info(f"Starting video generation for twin {twin_id}...")
        video_path = generate_talking_avatar(twin_id, audio_path)

        if video_path and os.path.exists(video_path):
            # Return relative URL for frontend
            rel_path = video_path.replace(os.sep, "/")
            # Convert storage/... to the static URL format
            if "storage" in rel_path:
                storage_rel = rel_path[rel_path.index("storage"):]
                video_url = f"/static/{storage_rel}"
            else:
                video_url = f"/static/{rel_path}"

            logger.info(f"✅ Video ready: {video_url}")
            return {
                "status": "success",
                "video_url": video_url,
                "message": "Video generated successfully"
            }
        else:
            return {
                "status": "unavailable",
                "video_url": "",
                "message": (
                    "Video generation tools not installed. "
                    "To enable: git clone https://github.com/OpenTalker/SadTalker next to your project folder. "
                    "Then run: pip install -r SadTalker/requirements.txt && bash SadTalker/scripts/download_models.sh"
                )
            }

    except Exception as e:
        logger.error(f"Video generation error: {e}")
        return {
            "status": "error",
            "message": str(e),
            "video_url": ""
        }


@router.get("/status/{twin_id}")
async def avatar_status(twin_id: str):
    """Check what avatar assets are available for a twin."""
    from avatar.video_generator import is_sadtalker_available, is_wav2lip_available, get_latest_video

    avatars_dir = os.path.join(settings.AVATARS_DIR, twin_id)
    emotions_available = []
    avatars_available = []
    for emotion in ["neutral", "happy", "sad", "angry"]:
        path = os.path.join(avatars_dir, f"{emotion}.jpg")
        avatar_path = os.path.join(avatars_dir, f"{emotion}_avatar.jpg")
        if os.path.exists(path):
            emotions_available.append(emotion)
        if os.path.exists(avatar_path):
            avatars_available.append(emotion)

    latest_video = get_latest_video(twin_id)
    video_url = ""
    if latest_video:
        rel = latest_video.replace(os.sep, "/")
        if "storage" in rel:
            video_url = f"/static/{rel[rel.index('storage'):]}"

    return {
        "twin_id": twin_id,
        "emotions_captured": emotions_available,
        "avatars_generated": avatars_available,
        "photos_ready": len(emotions_available),
        "avatars_ready": len(avatars_available),
        "sadtalker_available": is_sadtalker_available(),
        "wav2lip_available": is_wav2lip_available(),
        "video_generation_supported": is_sadtalker_available() or is_wav2lip_available(),
        "latest_video_url": video_url,
    }
