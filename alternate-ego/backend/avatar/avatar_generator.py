"""Avatar photo management - uses pre-stored team member avatars.

Strategy:
  1. Match the person's name to one of the 4 team members.
  2. If no match, use gender + name to determine which generic avatar set.
  3. Copy the matching pre-stored avatars to the twin's storage directory.

Result: 1 input photo -> 4 emotion avatar PNGs (neutral, happy, sad, angry).
"""
import base64
import logging
import os
import random
import shutil
from typing import Dict, Optional

from PIL import Image

from config import settings

logger = logging.getLogger(__name__)

EMOTIONS = ["neutral", "happy", "sad", "angry"]

PREBUILT_IMAGES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images"
)

TEAM_MEMBERS = {
    "prabhdeep singh narula": "02213202722",
    "prabhdeep singh": "02213202722",
    "pradeep singh narula": "02213202722",
    "pradeep singh": "02213202722",
    "prabhdeep": "02213202722",
    "aryan bains": "06513202722",
    "aryan": "06513202722",
    "japeen kaur sehgal": "09213202722",
    "japeen kaur": "09213202722",
    "japeen": "09213202722",
    "simardeep kaur bhatia": "02313202722",
    "simardeep kaur": "02313202722",
    "simardeep": "02313202722",
}

GENDER_FOLDERS = {
    "male_singh": "00313202722",
    "male_other": "00113202722",
    "female": ["00013202722", "00213202722"],
}

EMOTION_TO_FILENAME = {
    "neutral": "neutral",
    "happy": "smile",
    "sad": "sad",
    "angry": "angry",
}


def _find_team_member_folder(name: str) -> Optional[str]:
    """Find the pre-built avatar folder for a team member by name."""
    name_lower = name.strip().lower()

    for key in sorted(TEAM_MEMBERS.keys(), key=len, reverse=True):
        if key in name_lower or name_lower in key:
            folder = TEAM_MEMBERS[key]
            folder_path = os.path.join(PREBUILT_IMAGES_DIR, folder)
            if os.path.isdir(folder_path):
                logger.info("Team member matched: '%s' -> %s", name, folder)
                return folder_path

    return None


def _find_gender_folder(name: str, gender: str) -> str:
    """Find the correct fallback folder based on gender and name."""
    name_lower = name.strip().lower()
    gender_lower = gender.strip().lower()

    if gender_lower == "female":
        folder_name = random.choice(GENDER_FOLDERS["female"])
    elif "singh" in name_lower.split():
        folder_name = GENDER_FOLDERS["male_singh"]
    else:
        folder_name = GENDER_FOLDERS["male_other"]

    logger.info("Gender fallback: '%s' (gender=%s) -> %s", name, gender, folder_name)
    return os.path.join(PREBUILT_IMAGES_DIR, folder_name)


def _find_emotion_image(folder_path: str, emotion: str) -> Optional[str]:
    """Find the image file for a specific emotion in a folder."""
    emotion_keyword = EMOTION_TO_FILENAME.get(emotion, emotion)

    if not os.path.isdir(folder_path):
        return None

    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")) and emotion_keyword.lower() in filename.lower():
            return os.path.join(folder_path, filename)

    return None


def save_original_photo(twin_id: str, photo_bytes: bytes) -> str:
    """Save the single original captured photo."""
    avatar_dir = os.path.join(settings.AVATARS_DIR, twin_id)
    os.makedirs(avatar_dir, exist_ok=True)

    file_path = os.path.join(avatar_dir, "original.jpg")
    with open(file_path, "wb") as f:
        f.write(photo_bytes)

    neutral_path = os.path.join(avatar_dir, "neutral.jpg")
    with open(neutral_path, "wb") as f:
        f.write(photo_bytes)

    logger.info("Original photo saved: %s", file_path)
    return file_path


def save_original_photo_base64(twin_id: str, base64_data: str) -> str:
    """Save a base64-encoded original photo."""
    if "," in base64_data:
        base64_data = base64_data.split(",", 1)[1]
    photo_bytes = base64.b64decode(base64_data)
    return save_original_photo(twin_id, photo_bytes)


def generate_all_emotion_avatars(twin_id: str, name: str = "", gender: str = "male") -> Dict[str, str]:
    """Generate all emotion avatars by copying pre-stored images."""
    results: Dict[str, str] = {}
    avatar_dir = os.path.join(settings.AVATARS_DIR, twin_id)
    os.makedirs(avatar_dir, exist_ok=True)

    source_folder = _find_team_member_folder(name)
    if not source_folder:
        source_folder = _find_gender_folder(name, gender)

    if not source_folder or not os.path.isdir(source_folder):
        logger.error("Avatar source folder not found: %s", source_folder)
        return results

    logger.info("Using avatar source: %s", source_folder)

    for emotion in EMOTIONS:
        source_image = _find_emotion_image(source_folder, emotion)
        if not source_image:
            logger.warning("No %s image found in %s", emotion, source_folder)
            continue

        dest_path = os.path.join(avatar_dir, f"{emotion}_avatar.png")
        try:
            img = Image.open(source_image)
            img = img.resize((512, 512), Image.Resampling.LANCZOS)
            img.save(dest_path, "PNG")
            results[emotion] = dest_path
            logger.info("%s avatar copied from %s", emotion, os.path.basename(source_image))
        except Exception as exc:
            logger.error("Failed to copy %s avatar: %s", emotion, exc)

    logger.info("Avatar generation complete: %s/%s avatars from local images", len(results), len(EMOTIONS))
    return results


def generate_single_avatar(twin_id: str, emotion: str, name: str = "", gender: str = "male") -> str:
    """Generate a single emotion avatar by copying from pre-stored images."""
    avatar_dir = os.path.join(settings.AVATARS_DIR, twin_id)
    os.makedirs(avatar_dir, exist_ok=True)

    source_folder = _find_team_member_folder(name)
    if not source_folder:
        source_folder = _find_gender_folder(name, gender)

    if not source_folder or not os.path.isdir(source_folder):
        return ""

    source_image = _find_emotion_image(source_folder, emotion)
    if not source_image:
        return ""

    dest_path = os.path.join(avatar_dir, f"{emotion}_avatar.png")
    try:
        img = Image.open(source_image)
        img = img.resize((512, 512), Image.Resampling.LANCZOS)
        img.save(dest_path, "PNG")
        return dest_path
    except Exception as exc:
        logger.error("Failed to copy %s avatar: %s", emotion, exc)
        return ""


def detect_avatar_style(name: str) -> str:
    """Detect the avatar style based on the person's name."""
    name_lower = name.strip().lower()
    name_parts = name_lower.split()

    if "singh" in name_parts:
        return "sikh_boy"
    if "kaur" in name_parts:
        return "girl"
    return "boy"


def get_avatar_path(twin_id: str) -> str:
    """Get the default avatar path (neutral avatar preferred)."""
    for name in ["neutral_avatar.png", "neutral_avatar.jpg", "original.jpg", "neutral.jpg"]:
        path = os.path.join(settings.AVATARS_DIR, twin_id, name)
        if os.path.exists(path):
            return path
    return ""


def get_emotion_photo(twin_id: str, mood: str, prefer_avatar: bool = True) -> str:
    """Get the appropriate emotion avatar based on mood."""
    mood_to_emotion = {
        "happy": "happy",
        "excited": "happy",
        "sad": "sad",
        "angry": "angry",
        "frustrated": "angry",
        "neutral": "neutral",
        "thoughtful": "neutral",
    }
    emotion = mood_to_emotion.get(mood, "neutral")

    if prefer_avatar:
        for ext in ["png", "jpg"]:
            path = os.path.join(settings.AVATARS_DIR, twin_id, f"{emotion}_avatar.{ext}")
            if os.path.exists(path):
                return path

    for fallback in ["original.jpg", "neutral.jpg"]:
        path = os.path.join(settings.AVATARS_DIR, twin_id, fallback)
        if os.path.exists(path):
            return path
    return ""


def get_all_avatars(twin_id: str) -> Dict[str, str]:
    """Get all stored avatar paths."""
    avatars: Dict[str, str] = {}
    avatar_dir = os.path.join(settings.AVATARS_DIR, twin_id)

    original = os.path.join(avatar_dir, "original.jpg")
    if os.path.exists(original):
        avatars["original"] = original

    for emotion in EMOTIONS:
        for ext in ["png", "jpg"]:
            path = os.path.join(avatar_dir, f"{emotion}_avatar.{ext}")
            if os.path.exists(path):
                avatars[emotion] = path
                break

    return avatars


def get_all_photos(twin_id: str) -> Dict[str, str]:
    """Backward-compatible alias for stored avatar paths."""
    return get_all_avatars(twin_id)


def get_photos_count(twin_id: str) -> int:
    """Count how many avatar assets are stored."""
    return len(get_all_avatars(twin_id))


def delete_photos(twin_id: str):
    """Delete all photos for a twin."""
    avatar_dir = os.path.join(settings.AVATARS_DIR, twin_id)
    if os.path.exists(avatar_dir):
        shutil.rmtree(avatar_dir)
        logger.info("Deleted avatar photos: %s", avatar_dir)


def save_photo(twin_id: str, emotion: str, photo_bytes: bytes) -> str:
    """Backward-compatible alias for the old multi-photo flow."""
    return save_original_photo(twin_id, photo_bytes)


def save_photo_base64(twin_id: str, emotion: str, base64_data: str) -> str:
    """Backward-compatible alias for the old multi-photo flow."""
    return save_original_photo_base64(twin_id, base64_data)


def regenerate_all_avatars(twin_id: str):
    """Backward-compatible alias for regenerating the local avatar set."""
    generate_all_emotion_avatars(twin_id)
