"""Onboarding API endpoints - handles the full twin creation flow."""
import json
import logging
import os
import uuid
from typing import List

from fastapi import APIRouter, BackgroundTasks, File, Form, UploadFile
from pydantic import BaseModel

from avatar.avatar_generator import (
    generate_all_emotion_avatars,
    get_all_avatars,
    save_original_photo_base64,
)
from config import settings
from db.database import (
    _row_to_dict,
    create_onboarding_session,
    create_twin,
    create_user,
    get_connection,
    get_onboarding,
    get_twin,
    update_onboarding,
    update_twin,
)
from db.models import OnboardingStatus, StartRequest, StartResponse
from rag.prompt_builder import build_system_prompt
from rag.scrape_processor import parse_data_export, scrape_and_index
from rag.transcript_processor import (
    ALL_QUESTIONS,
    INTERVIEW_QUESTIONS,
    extract_personality_from_transcripts,
    get_random_questions,
    process_transcripts,
)
from security.encryption import encrypt_file
from voice.stt import transcribe
from voice.voice_manager import save_interview_audio

logger = logging.getLogger(__name__)
router = APIRouter()


def _get_user_record(user_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        return _row_to_dict(cursor, cursor.fetchone())
    finally:
        cursor.close()
        conn.close()


@router.post("/start", response_model=StartResponse)
async def start_onboarding(req: StartRequest):
    """Start the onboarding process and create user, twin, and session IDs."""
    user_id = str(uuid.uuid4())
    twin_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())

    social_urls = json.dumps(
        {
            "linkedin": req.linkedin_url,
            "instagram": req.instagram_url,
            "twitter": req.twitter_url,
            "facebook": req.facebook_url,
            "other": req.other_url,
        }
    )

    create_user(user_id, req.name, social_urls, req.email, req.phone)
    create_twin(twin_id, user_id)
    create_onboarding_session(session_id, user_id, twin_id)

    logger.info("Onboarding started: user=%s, twin=%s", user_id, twin_id)
    return StartResponse(
        user_id=user_id,
        twin_id=twin_id,
        session_id=session_id,
        message=f"Welcome, {req.name}! Your digital twin creation has begun.",
    )


@router.post("/scrape")
async def scrape_social(
    twin_id: str = Form(...),
    session_id: str = Form(...),
    name: str = Form(...),
    linkedin_url: str = Form(""),
    instagram_url: str = Form(""),
    twitter_url: str = Form(""),
    facebook_url: str = Form(""),
    other_url: str = Form(""),
    background_tasks: BackgroundTasks = None,
):
    """Scrape the provided social links and index the extracted knowledge."""
    del background_tasks
    update_onboarding(session_id, scraping_status="in_progress")

    other_urls = [value.strip() for value in other_url.split(",") if value.strip()] if other_url.strip() else []
    urls = [value for value in [linkedin_url, instagram_url, twitter_url, facebook_url] if value.strip()]
    urls.extend(other_urls)

    try:
        result = scrape_and_index(name, twin_id, urls, session_id=session_id)
        update_onboarding(session_id, scraping_status="done")
        return {"status": "success", **result}
    except Exception as exc:
        update_onboarding(session_id, scraping_status="failed")
        logger.error("Scraping failed: %s", exc)
        return {"status": "failed", "error": str(exc), "chunks_indexed": 0}


@router.post("/upload-photo")
async def upload_photo(
    twin_id: str = Form(...),
    session_id: str = Form(...),
    emotion: str = Form("neutral"),
    photo: str = Form(...),
):
    """Upload one photo and generate the full local avatar set."""
    del emotion
    try:
        path = save_original_photo_base64(twin_id, photo)
        original_url = f"/static/{path.replace(os.sep, '/')}"
        update_onboarding(session_id, photos_captured=1)

        avatar_urls = {}
        try:
            results = generate_all_emotion_avatars(twin_id)
            all_avatars = get_all_avatars(twin_id)
            avatar_urls = {key: f"/static/{avatar_path.replace(os.sep, '/')}" for key, avatar_path in all_avatars.items()}
            update_onboarding(session_id, photos_captured=len(results) + 1)
        except Exception as exc:
            logger.warning("Avatar generation failed (non-critical): %s", exc)

        return {
            "status": "success",
            "original_url": original_url,
            "avatar_urls": avatar_urls,
            "avatars_generated": len(avatar_urls),
            "path": path,
        }
    except Exception as exc:
        logger.error("Photo upload failed: %s", exc)
        return {"status": "error", "message": str(exc)}


@router.post("/upload-voice")
async def upload_voice(
    twin_id: str = Form(...),
    session_id: str = Form(...),
    question_index: int = Form(...),
    question_text: str = Form(""),
    audio: UploadFile = File(...),
):
    """Upload one voice interview recording and transcribe it."""
    del question_text
    try:
        audio_bytes = await audio.read()
        audio_path = save_interview_audio(twin_id, audio_bytes, question_index)
        transcript = transcribe(audio_path)
        question = INTERVIEW_QUESTIONS[question_index] if question_index < len(INTERVIEW_QUESTIONS) else f"Question {question_index + 1}"

        update_onboarding(session_id, questions_answered=question_index + 1)
        return {
            "status": "success",
            "question_index": question_index,
            "transcript": transcript,
            "question": question,
        }
    except Exception as exc:
        logger.error("Voice upload failed: %s", exc)
        return {"status": "error", "message": str(exc)}


@router.post("/upload-data")
async def upload_data_export(
    twin_id: str = Form(...),
    session_id: str = Form(...),
    file: UploadFile = File(...),
):
    """Upload and index a social media data export."""
    del session_id
    try:
        upload_dir = os.path.join(settings.UPLOADS_DIR, twin_id)
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())

        result = parse_data_export(file_path, twin_id)
        try:
            encrypt_file(file_path)
        except Exception:
            if os.path.exists(file_path):
                os.remove(file_path)

        return {"status": "success", **result}
    except Exception as exc:
        logger.error("Data upload failed: %s", exc)
        return {"status": "error", "message": str(exc)}


@router.post("/complete")
async def complete_onboarding(
    twin_id: str = Form(...),
    session_id: str = Form(...),
    transcripts: str = Form("[]"),
):
    """Process transcripts, enrich personality, and activate the twin."""
    try:
        transcript_list = json.loads(transcripts) if transcripts else []
        twin = get_twin(twin_id)
        if not twin:
            return {"status": "error", "message": "Twin not found"}

        user = _get_user_record(twin.get("user_id", "")) or {}
        name = user.get("name", "User")

        trivia_path = os.path.join(settings.UPLOADS_DIR, twin_id, "trivia", "trivia_answers.json")
        if os.path.exists(trivia_path):
            try:
                with open(trivia_path, "r", encoding="utf-8") as f:
                    for item in json.load(f):
                        transcript_list.append(
                            {"question": item.get("question", ""), "answer": item.get("answer", "")}
                        )
            except Exception as exc:
                logger.warning("Failed to load trivia answers: %s", exc)

        personality = {}
        if transcript_list:
            process_transcripts(twin_id, transcript_list)
            personality = extract_personality_from_transcripts(transcript_list)

        try:
            from voice.voice_manager import create_voice_reference

            ref_path = create_voice_reference(twin_id)
            if ref_path:
                logger.info("Voice reference created: %s", ref_path)
        except Exception as exc:
            logger.warning("Voice reference creation failed (non-critical): %s", exc)

        try:
            generate_all_emotion_avatars(twin_id, name=name)
            logger.info("Avatar generation complete for twin %s", twin_id)
        except Exception as exc:
            logger.warning("Avatar regeneration failed (non-critical): %s", exc)

        try:
            from avatar.vision_analyzer import extract_personality_from_faces

            vision_traits = extract_personality_from_faces(twin_id)
            if vision_traits:
                personality["facial_analysis"] = vision_traits
        except Exception as exc:
            logger.warning("Vision analysis failed (non-critical): %s", exc)

        system_prompt = build_system_prompt(name, personality)
        update_twin(
            twin_id,
            personality_profile=json.dumps(personality),
            system_prompt=system_prompt,
            status="active",
        )
        update_onboarding(session_id, status="complete")

        logger.info("Onboarding complete for twin %s", twin_id)
        return {
            "status": "success",
            "twin_id": twin_id,
            "message": "Your digital twin is ready! Chat with yourself now.",
            "personality": personality,
        }
    except Exception as exc:
        logger.error("Completion failed: %s", exc)
        return {"status": "error", "message": str(exc)}


class TriviaItem(BaseModel):
    id: int
    question: str
    answer: str
    type: str


class TriviaRequest(BaseModel):
    twin_id: str
    session_id: str
    trivia: List[TriviaItem]


@router.post("/save-trivia")
async def save_trivia(req: TriviaRequest):
    """Save trivia quiz answers for personality enrichment."""
    try:
        trivia_dir = os.path.join(settings.UPLOADS_DIR, req.twin_id, "trivia")
        os.makedirs(trivia_dir, exist_ok=True)

        filepath = os.path.join(trivia_dir, "trivia_answers.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(
                [item.model_dump() if hasattr(item, "model_dump") else item.dict() for item in req.trivia],
                f,
                ensure_ascii=False,
                indent=2,
            )

        logger.info("Saved trivia answers for twin %s", req.twin_id)
        return {"status": "success"}
    except Exception as exc:
        logger.error("Failed to save trivia: %s", exc)
        return {"status": "error", "message": str(exc)}


class GameScoreRequest(BaseModel):
    twin_id: str
    session_id: str
    game: str
    score: int
    hi_score: int


@router.post("/save-game-scores")
async def save_game_scores(req: GameScoreRequest):
    """Save lightweight game scores for later personality enrichment."""
    try:
        upload_dir = os.path.join(settings.UPLOADS_DIR, req.twin_id, "games")
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, f"{req.game}_scores.json")

        existing = []
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                existing = json.load(f)

        existing.append(
            {
                "score": req.score,
                "hi_score": req.hi_score,
                "session_id": req.session_id,
                "timestamp": str(uuid.uuid4())[:8],
            }
        )

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)

        analysis = {}
        if req.game == "pong":
            analysis = {
                "reflexes": "fast" if req.hi_score > 30 else "moderate" if req.hi_score > 15 else "developing",
                "hand_eye_coordination": "excellent" if req.hi_score > 40 else "good" if req.hi_score > 20 else "average",
                "persistence": "high" if len(existing) > 3 else "moderate",
            }
        elif req.game == "bubble":
            analysis = {
                "strategic_thinking": "strong" if req.hi_score > 500 else "moderate" if req.hi_score > 200 else "developing",
                "pattern_recognition": "excellent" if req.hi_score > 800 else "good" if req.hi_score > 300 else "average",
                "persistence": "high" if len(existing) > 3 else "moderate",
            }

        logger.info("Game score saved: %s=%s (hi=%s) for twin %s", req.game, req.score, req.hi_score, req.twin_id)
        return {"status": "success", "analysis": analysis}
    except Exception as exc:
        logger.error("Game score save failed: %s", exc)
        return {"status": "error", "message": str(exc)}


@router.get("/status/{session_id}", response_model=OnboardingStatus)
async def get_status(session_id: str):
    """Return current onboarding progress."""
    session = get_onboarding(session_id)
    if not session:
        return OnboardingStatus(
            session_id=session_id,
            scraping_status="unknown",
            photos_captured=0,
            questions_answered=0,
            avatar_status="unknown",
            voice_clone_status="unknown",
            status="not_found",
        )

    return OnboardingStatus(
        session_id=session_id,
        scraping_status=session.get("scraping_status", "pending"),
        photos_captured=session.get("photos_captured", 0),
        questions_answered=session.get("questions_answered", 0),
        avatar_status=session.get("avatar_status", "pending"),
        voice_clone_status=session.get("voice_clone_status", "pending"),
        status=session.get("status", "in_progress"),
    )


@router.get("/questions")
async def get_interview_questions(twin_id: str = None, count: int = 10):
    """Get randomized voice interview questions from the question bank."""
    questions = get_random_questions(count=count, seed=twin_id)
    return {
        "questions": questions,
        "total": len(questions),
        "max_seconds_per_question": 120,
        "total_questions_in_bank": 100,
    }


@router.post("/refresh-question")
async def refresh_question(exclude: str = Form("[]")):
    """Get a new question that is not already in the current visible set."""
    import random as rng

    try:
        exclude_list = json.loads(exclude) if exclude else []
    except Exception:
        exclude_list = []

    available = [question for question in ALL_QUESTIONS if question["text"] not in exclude_list]
    if not available:
        available = ALL_QUESTIONS

    chosen = rng.choice(available)
    return {
        "question": {
            "text": chosen["text"],
            "category": chosen["category"],
            "max_seconds": 120,
        }
    }


@router.post("/replace-voice")
async def replace_voice(
    twin_id: str = Form(...),
    session_id: str = Form(...),
    question_index: int = Form(...),
    question_text: str = Form(""),
    audio: UploadFile = File(...),
):
    """Replace a previously recorded voice answer and re-transcribe it."""
    del session_id, question_text
    try:
        audio_bytes = await audio.read()
        audio_path = save_interview_audio(twin_id, audio_bytes, question_index)
        transcript = transcribe(audio_path)
        question = INTERVIEW_QUESTIONS[question_index] if question_index < len(INTERVIEW_QUESTIONS) else f"Question {question_index + 1}"
        return {
            "status": "success",
            "question_index": question_index,
            "transcript": transcript,
            "question": question,
        }
    except Exception as exc:
        logger.error("Voice replace failed: %s", exc)
        return {"status": "error", "message": str(exc)}
