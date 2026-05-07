"""Avatar API - photo upload, avatar generation, and video endpoints."""
import logging
import os

from fastapi import APIRouter
from pydantic import BaseModel

from config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


class VideoRequest(BaseModel):
    twin_id: str
    text: str


class GenerateAvatarsRequest(BaseModel):
    twin_id: str
    name: str = ""
    gender: str = "male"


class SinglePhotoUploadRequest(BaseModel):
    twin_id: str
    session_id: str
    photo: str


@router.post("/upload-single-photo")
async def upload_single_photo(req: SinglePhotoUploadRequest):
    """Save a single original photo before avatar generation."""
    from avatar.avatar_generator import save_original_photo_base64

    try:
        path = save_original_photo_base64(req.twin_id, req.photo)
        photo_url = f"/static/{path.replace(os.sep, '/')}"
        return {
            "status": "success",
            "original_url": photo_url,
            "message": "Original photo saved. Ready for avatar generation.",
        }
    except Exception as exc:
        logger.error("Photo upload failed: %s", exc)
        return {"status": "error", "message": str(exc)}


@router.post("/generate-all")
async def generate_all_avatars(req: GenerateAvatarsRequest):
    """Generate all four emotion avatars from the local image library."""
    from avatar.avatar_generator import generate_all_emotion_avatars, get_all_avatars

    try:
        results = generate_all_emotion_avatars(req.twin_id, name=req.name, gender=req.gender)
        all_avatars = get_all_avatars(req.twin_id)
        avatar_urls = {key: f"/static/{path.replace(os.sep, '/')}" for key, path in all_avatars.items()}
        return {
            "status": "success",
            "avatars_generated": len(results),
            "avatar_urls": avatar_urls,
            "message": f"Generated {len(results)} emotion avatars successfully!",
        }
    except Exception as exc:
        logger.error("Avatar generation failed: %s", exc)
        return {
            "status": "error",
            "message": str(exc),
            "avatars_generated": 0,
            "avatar_urls": {},
        }


@router.post("/generate-single")
async def generate_single_emotion(twin_id: str, emotion: str, name: str = "", gender: str = "male"):
    """Generate a single emotion avatar."""
    from avatar.avatar_generator import generate_single_avatar

    try:
        path = generate_single_avatar(twin_id, emotion, name=name, gender=gender)
        if not path:
            return {"status": "error", "message": f"Failed to generate {emotion} avatar"}
        return {
            "status": "success",
            "emotion": emotion,
            "avatar_url": f"/static/{path.replace(os.sep, '/')}",
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@router.post("/generate-video")
async def generate_video_avatar(req: VideoRequest):
    """Generate a lip-synced talking-head video for the latest TTS audio."""
    from avatar.video_generator import generate_talking_avatar
    from voice.tts import generate_speech

    try:
        logger.info("Generating TTS audio for video: %s...", req.text[:60])
        audio_path = generate_speech(req.text[:300], req.twin_id)
        if not audio_path:
            return {
                "status": "error",
                "message": "Could not generate TTS audio. Check that ElevenLabs is configured correctly.",
                "video_url": "",
            }

        logger.info("Starting video generation for twin %s...", req.twin_id)
        video_path = generate_talking_avatar(req.twin_id, audio_path)
        if not video_path or not os.path.exists(video_path):
            return {
                "status": "unavailable",
                "video_url": "",
                "message": (
                    "Video generation tools not installed. "
                    "To enable: git clone https://github.com/OpenTalker/SadTalker next to your project folder. "
                    "Then run: pip install -r SadTalker/requirements.txt && bash SadTalker/scripts/download_models.sh"
                ),
            }

        rel_path = video_path.replace(os.sep, "/")
        if "storage" in rel_path:
            rel_path = rel_path[rel_path.index("storage"):]
        video_url = f"/static/{rel_path}"
        logger.info("Video ready: %s", video_url)
        return {"status": "success", "video_url": video_url, "message": "Video generated successfully"}
    except Exception as exc:
        logger.error("Video generation error: %s", exc)
        return {"status": "error", "message": str(exc), "video_url": ""}


@router.get("/status/{twin_id}")
async def avatar_status(twin_id: str):
    """Check what avatar and video assets are available for a twin."""
    from avatar.avatar_generator import get_all_avatars
    from avatar.video_generator import get_latest_video, is_sadtalker_available, is_wav2lip_available

    avatars = get_all_avatars(twin_id)
    avatar_urls = {key: f"/static/{path.replace(os.sep, '/')}" for key, path in avatars.items()}
    emotions_available = [emotion for emotion in ["neutral", "happy", "sad", "angry"] if emotion in avatars]

    avatars_dir = os.path.join(settings.AVATARS_DIR, twin_id)
    emotions_captured = []
    for emotion in ["neutral", "happy", "sad", "angry"]:
        if os.path.exists(os.path.join(avatars_dir, f"{emotion}.jpg")):
            emotions_captured.append(emotion)

    latest_video = get_latest_video(twin_id)
    video_url = ""
    if latest_video:
        rel = latest_video.replace(os.sep, "/")
        if "storage" in rel:
            rel = rel[rel.index("storage"):]
        video_url = f"/static/{rel}"

    return {
        "twin_id": twin_id,
        "has_original": "original" in avatars,
        "emotions_available": emotions_available,
        "avatars_generated": len(emotions_available),
        "avatar_urls": avatar_urls,
        "emotions_captured": emotions_captured,
        "photos_ready": len(emotions_captured),
        "avatars_ready": len(emotions_available),
        "sadtalker_available": is_sadtalker_available(),
        "wav2lip_available": is_wav2lip_available(),
        "video_generation_supported": is_sadtalker_available() or is_wav2lip_available(),
        "latest_video_url": video_url,
    }


@router.get("/emotion/{twin_id}/{mood}")
async def get_emotion_avatar(twin_id: str, mood: str):
    """Get the best avatar URL for a detected mood."""
    from avatar.avatar_generator import get_emotion_photo

    path = get_emotion_photo(twin_id, mood, prefer_avatar=True)
    if not path:
        return {"mood": mood, "avatar_url": ""}
    return {"mood": mood, "avatar_url": f"/static/{path.replace(os.sep, '/')}"}
