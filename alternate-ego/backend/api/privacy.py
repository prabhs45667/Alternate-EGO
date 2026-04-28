"""Privacy API — data deletion and summary endpoints."""
from fastapi import APIRouter
from db.database import get_twin, get_connection
from db.models import DataSummary, DeleteResponse
from security.encryption import delete_securely
from rag.vector_store import get_chunk_count
from avatar.avatar_generator import get_photos_count

router = APIRouter()


@router.delete("/delete-all/{twin_id}", response_model=DeleteResponse)
async def delete_all_data(twin_id: str):
    """Permanently delete ALL data for a twin."""
    twin = get_twin(twin_id)
    if not twin:
        return DeleteResponse(
            status="error",
            twin_id=twin_id,
            items_deleted={}
        )

    deleted = delete_securely(twin_id)

    # Also clean up database records
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Delete messages first (foreign key)
        cursor.execute("""
            DELETE FROM messages WHERE conversation_id IN (
                SELECT id FROM conversations WHERE twin_id = %s
            )
        """, (twin_id,))
        cursor.execute("DELETE FROM conversations WHERE twin_id = %s", (twin_id,))
        cursor.execute("DELETE FROM onboarding_sessions WHERE twin_id = %s", (twin_id,))
        cursor.execute("DELETE FROM twins WHERE id = %s", (twin_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return DeleteResponse(
        status="All data permanently deleted",
        twin_id=twin_id,
        items_deleted=deleted
    )


@router.get("/data-summary/{twin_id}", response_model=DataSummary)
async def data_summary(twin_id: str):
    """Get a summary of what data is stored for a twin."""
    photos = get_photos_count(twin_id)
    chunks = get_chunk_count(twin_id)

    # Count conversations and messages
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as c FROM conversations WHERE twin_id = %s", (twin_id,))
    conv_count = cursor.fetchone()[0]
    cursor.execute("""
        SELECT COUNT(*) as c FROM messages WHERE conversation_id IN (
            SELECT id FROM conversations WHERE twin_id = %s
        )
    """, (twin_id,))
    msg_count = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    return DataSummary(
        twin_id=twin_id,
        photos_stored=photos,
        voice_samples=1 if photos > 0 else 0,
        rag_chunks=chunks,
        conversations=conv_count,
        messages=msg_count
    )
