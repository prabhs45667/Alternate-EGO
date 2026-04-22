"""Avatar photo management — saves 4 emotion photos + generates cartoon avatars."""
import os
import base64
import logging
from typing import Dict, Optional
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import numpy as np
from config import settings

logger = logging.getLogger(__name__)

EMOTIONS = ["neutral", "happy", "sad", "angry"]


def save_photo(twin_id: str, emotion: str, photo_bytes: bytes) -> str:
    """Save an emotion photo for a twin.
    
    Args:
        twin_id: Twin ID
        emotion: One of 'neutral', 'happy', 'sad', 'angry'
        photo_bytes: Raw image bytes (JPEG/PNG)
    
    Returns:
        Path to saved photo
    """
    if emotion not in EMOTIONS:
        raise ValueError(f"Invalid emotion: {emotion}. Must be one of {EMOTIONS}")
    
    avatar_dir = os.path.join(settings.AVATARS_DIR, twin_id)
    os.makedirs(avatar_dir, exist_ok=True)
    
    file_path = os.path.join(avatar_dir, f"{emotion}.jpg")
    with open(file_path, 'wb') as f:
        f.write(photo_bytes)
    
    logger.info(f"✅ Photo saved: {file_path}")
    
    # Auto-generate avatar (cartoon) version
    try:
        avatar_path = create_avatar_style(twin_id, emotion)
        if avatar_path:
            logger.info(f"✅ Avatar generated: {avatar_path}")
    except Exception as e:
        logger.warning(f"Avatar generation failed (non-critical): {e}")
    
    return file_path


def save_photo_base64(twin_id: str, emotion: str, base64_data: str) -> str:
    """Save a base64-encoded photo."""
    # Strip data URL prefix if present
    if ',' in base64_data:
        base64_data = base64_data.split(',')[1]
    
    photo_bytes = base64.b64decode(base64_data)
    return save_photo(twin_id, emotion, photo_bytes)


def create_avatar_style(twin_id: str, emotion: str) -> str:
    """Convert a photo to a cartoon/avatar style using Pillow image processing.
    
    This creates a stylized avatar that looks like a digital art/cartoon version
    of the person — similar to Snapchat's cartoon filters.
    
    Pipeline:
    1. Resize for consistent processing
    2. Color quantization (reduce to limited palette for cartoon look)
    3. Edge detection for cartoon outlines
    4. Bilateral-style smoothing (simulated via multiple blur+sharpen passes)
    5. Saturation and contrast boost for vibrant look
    6. Combine edges with smoothed/posterized image
    
    Returns:
        Path to the generated avatar image
    """
    avatar_dir = os.path.join(settings.AVATARS_DIR, twin_id)
    source_path = os.path.join(avatar_dir, f"{emotion}.jpg")
    avatar_path = os.path.join(avatar_dir, f"{emotion}_avatar.jpg")
    
    if not os.path.exists(source_path):
        return ""
    
    try:
        img = Image.open(source_path).convert("RGB")
        
        # 1. Resize to consistent size for processing
        img = img.resize((512, 512), Image.Resampling.LANCZOS)
        
        # 2. Smooth the image (simulate bilateral filter with multiple passes)
        smooth = img.copy()
        for _ in range(7):
            smooth = smooth.filter(ImageFilter.MedianFilter(size=5))
        smooth = smooth.filter(ImageFilter.SMOOTH_MORE)
        
        # 3. Color quantization — reduce to limited color palette (cartoon effect)
        # Convert to numpy for quantization
        img_array = np.array(smooth, dtype=np.float32)
        
        # Posterize: reduce color levels (more dramatic = more cartoony)
        num_levels = 8
        img_array = np.floor(img_array / (256 / num_levels)) * (256 / num_levels)
        img_array = np.clip(img_array, 0, 255).astype(np.uint8)
        
        cartoon = Image.fromarray(img_array)
        
        # 4. Edge detection for outlines
        gray = img.convert("L")
        # Use multiple edge passes for thick cartoon outlines
        edges1 = gray.filter(ImageFilter.FIND_EDGES)
        edges2 = gray.filter(ImageFilter.Kernel((3, 3), [-1, -1, -1, -1, 8, -1, -1, -1, -1], scale=1, offset=128))
        
        # Threshold edges to create clean black outlines
        edges1_array = np.array(edges1)
        edges2_array = np.array(edges2)
        
        # Combine edge maps
        combined_edges = np.maximum(edges1_array, np.abs(edges2_array.astype(np.int16) - 128).astype(np.uint8))
        
        # Threshold: strong edges become black outlines
        edge_threshold = 30
        edge_mask = (combined_edges > edge_threshold).astype(np.uint8) * 255
        
        # Dilate edges slightly for thicker outlines
        edge_img = Image.fromarray(255 - edge_mask)  # Invert: white bg, black lines
        edge_img = edge_img.filter(ImageFilter.MinFilter(size=3))  # Thicken lines
        
        # 5. Combine cartoon colors with edges
        # Convert edge image to RGB
        edge_rgb = edge_img.convert("RGB")
        edge_array = np.array(edge_rgb, dtype=np.float32) / 255.0
        cartoon_array = np.array(cartoon, dtype=np.float32)
        
        # Multiply cartoon with edge mask (edges darken the image)
        result_array = (cartoon_array * edge_array).astype(np.uint8)
        result = Image.fromarray(result_array)
        
        # 6. Boost saturation and contrast for vibrant look
        enhancer = ImageEnhance.Color(result)
        result = enhancer.enhance(1.4)  # Boost saturation
        
        enhancer = ImageEnhance.Contrast(result)
        result = enhancer.enhance(1.2)  # Boost contrast
        
        enhancer = ImageEnhance.Brightness(result)
        result = enhancer.enhance(1.05)  # Slight brightness boost
        
        # 7. Final smooth pass to blend everything
        result = result.filter(ImageFilter.SMOOTH)
        
        # 8. Add subtle vignette effect
        result = _add_vignette(result)
        
        # Save avatar
        result.save(avatar_path, "JPEG", quality=92)
        logger.info(f"✅ Cartoon avatar created: {avatar_path}")
        return avatar_path
        
    except Exception as e:
        logger.error(f"Avatar stylization error: {e}")
        return ""


def _add_vignette(img: Image.Image) -> Image.Image:
    """Add a subtle vignette (dark corners) effect."""
    try:
        width, height = img.size
        # Create radial gradient mask
        x = np.linspace(-1, 1, width)
        y = np.linspace(-1, 1, height)
        X, Y = np.meshgrid(x, y)
        radius = np.sqrt(X**2 + Y**2)
        
        # Vignette: fade to 0.7 at corners
        vignette = 1.0 - np.clip((radius - 0.7) / 0.8, 0, 0.3)
        
        # Apply vignette
        img_array = np.array(img, dtype=np.float32)
        for c in range(3):
            img_array[:, :, c] *= vignette
        
        return Image.fromarray(np.clip(img_array, 0, 255).astype(np.uint8))
    except Exception:
        return img


def regenerate_all_avatars(twin_id: str):
    """Regenerate cartoon avatars for all existing photos of a twin."""
    for emotion in EMOTIONS:
        try:
            create_avatar_style(twin_id, emotion)
        except Exception as e:
            logger.warning(f"Failed to regenerate {emotion} avatar: {e}")


def get_avatar_path(twin_id: str) -> str:
    """Get the default avatar path (neutral photo — avatar version preferred)."""
    avatar_path = os.path.join(settings.AVATARS_DIR, twin_id, "neutral_avatar.jpg")
    if os.path.exists(avatar_path):
        return avatar_path
    # Fallback to raw photo
    path = os.path.join(settings.AVATARS_DIR, twin_id, "neutral.jpg")
    return path if os.path.exists(path) else ""


def get_emotion_photo(twin_id: str, mood: str, prefer_avatar: bool = True) -> str:
    """Get the appropriate emotion photo based on mood.
    
    Maps detected moods to the 4 stored emotions.
    If prefer_avatar=True, returns the cartoon avatar version.
    """
    mood_to_emotion = {
        "happy": "happy",
        "excited": "happy",
        "sad": "sad",
        "angry": "angry",
        "frustrated": "angry",
        "neutral": "neutral",
        "thoughtful": "neutral"
    }
    
    emotion = mood_to_emotion.get(mood, "neutral")
    
    if prefer_avatar:
        # Try avatar version first
        avatar_path = os.path.join(settings.AVATARS_DIR, twin_id, f"{emotion}_avatar.jpg")
        if os.path.exists(avatar_path):
            return avatar_path
    
    # Fallback to raw photo
    path = os.path.join(settings.AVATARS_DIR, twin_id, f"{emotion}.jpg")
    
    if os.path.exists(path):
        return path
    
    # Fallback to neutral
    if prefer_avatar:
        neutral_avatar = os.path.join(settings.AVATARS_DIR, twin_id, "neutral_avatar.jpg")
        if os.path.exists(neutral_avatar):
            return neutral_avatar
    
    neutral_path = os.path.join(settings.AVATARS_DIR, twin_id, "neutral.jpg")
    return neutral_path if os.path.exists(neutral_path) else ""


def get_all_photos(twin_id: str) -> Dict[str, str]:
    """Get all stored emotion photo paths (prefer avatar versions)."""
    photos = {}
    for emotion in EMOTIONS:
        # Try avatar version first
        avatar_path = os.path.join(settings.AVATARS_DIR, twin_id, f"{emotion}_avatar.jpg")
        if os.path.exists(avatar_path):
            photos[emotion] = avatar_path
        else:
            path = os.path.join(settings.AVATARS_DIR, twin_id, f"{emotion}.jpg")
            if os.path.exists(path):
                photos[emotion] = path
    return photos


def get_photos_count(twin_id: str) -> int:
    """Count how many emotion photos are stored."""
    count = 0
    for emotion in EMOTIONS:
        path = os.path.join(settings.AVATARS_DIR, twin_id, f"{emotion}.jpg")
        if os.path.exists(path):
            count += 1
    return count


def delete_photos(twin_id: str):
    """Delete all photos for a twin."""
    import shutil
    avatar_dir = os.path.join(settings.AVATARS_DIR, twin_id)
    if os.path.exists(avatar_dir):
        shutil.rmtree(avatar_dir)
        logger.info(f"🗑️ Deleted avatar photos: {avatar_dir}")
