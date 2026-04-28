"""PostgreSQL (NeonDB) database initialization and helper functions."""
import os
import logging
import psycopg2
import psycopg2.extras
from config import settings

logger = logging.getLogger(__name__)


def get_connection():
    """Get a new PostgreSQL connection."""
    conn = psycopg2.connect(settings.DATABASE_URL)
    return conn


def _row_to_dict(cursor, row):
    """Convert a psycopg2 row to dict using cursor description."""
    if row is None:
        return None
    columns = [desc[0] for desc in cursor.description]
    return dict(zip(columns, row))


def _rows_to_dicts(cursor, rows):
    if not rows:
        return []
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in rows]


def init_db():
    """Initialize the database with all required tables."""
    conn = get_connection()
    cursor = conn.cursor()
    statements = [
        """
        CREATE TABLE IF NOT EXISTS auth_accounts (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            user_id TEXT,
            twin_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            social_urls TEXT DEFAULT '{}',
            email TEXT DEFAULT '',
            phone TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS twins (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            voice_model_path TEXT,
            photo_neutral TEXT,
            photo_happy TEXT,
            photo_sad TEXT,
            photo_angry TEXT,
            avatar_path TEXT,
            personality_profile TEXT DEFAULT '{}',
            system_prompt TEXT DEFAULT '',
            scraped_data TEXT DEFAULT '{}',
            status TEXT DEFAULT 'creating',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            twin_id TEXT NOT NULL REFERENCES twins(id) ON DELETE CASCADE,
            title TEXT DEFAULT 'New Chat',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            sources TEXT DEFAULT '[]',
            mood TEXT DEFAULT 'neutral',
            audio_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS onboarding_sessions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            twin_id TEXT REFERENCES twins(id),
            scraping_status TEXT DEFAULT 'pending',
            photos_captured INTEGER DEFAULT 0,
            questions_answered INTEGER DEFAULT 0,
            avatar_status TEXT DEFAULT 'pending',
            voice_clone_status TEXT DEFAULT 'pending',
            status TEXT DEFAULT 'in_progress',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        "CREATE INDEX IF NOT EXISTS idx_twins_user ON twins(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_conversations_twin ON conversations(twin_id)",
        "CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id)",
        "CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(created_at)",
        "CREATE INDEX IF NOT EXISTS idx_onboarding_user ON onboarding_sessions(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_auth_email ON auth_accounts(email)",
    ]
    for stmt in statements:
        cursor.execute(stmt)
    conn.commit()
    cursor.close()
    conn.close()
    logger.info("PostgreSQL database initialized")



# --- Auth Account Functions ---

def create_auth_account(account_id: str, email: str, password_hash: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO auth_accounts (id, email, password_hash) VALUES (%s, %s, %s)",
        (account_id, email, password_hash)
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_auth_account_by_email(email: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM auth_accounts WHERE email = %s", (email,))
    row = cursor.fetchone()
    result = _row_to_dict(cursor, row)
    cursor.close()
    conn.close()
    return result


def get_auth_account_by_id(account_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM auth_accounts WHERE id = %s", (account_id,))
    row = cursor.fetchone()
    result = _row_to_dict(cursor, row)
    cursor.close()
    conn.close()
    return result


def update_auth_account(account_id: str, **kwargs):
    conn = get_connection()
    cursor = conn.cursor()
    set_clause = ", ".join(f"{k} = %s" for k in kwargs.keys())
    values = list(kwargs.values()) + [account_id]
    cursor.execute(f"UPDATE auth_accounts SET {set_clause} WHERE id = %s", values)
    conn.commit()
    cursor.close()
    conn.close()


# --- Helper Functions ---

def create_user(user_id: str, name: str, social_urls: str = "{}", email: str = "", phone: str = ""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (id, name, social_urls, email, phone) VALUES (%s, %s, %s, %s, %s)",
        (user_id, name, social_urls, email, phone)
    )
    conn.commit()
    cursor.close()
    conn.close()


def create_twin(twin_id: str, user_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO twins (id, user_id) VALUES (%s, %s)", (twin_id, user_id))
    conn.commit()
    cursor.close()
    conn.close()


def update_twin(twin_id: str, **kwargs):
    conn = get_connection()
    cursor = conn.cursor()
    set_clause = ", ".join(f"{k} = %s" for k in kwargs.keys())
    values = list(kwargs.values()) + [twin_id]
    cursor.execute(f"UPDATE twins SET {set_clause} WHERE id = %s", values)
    conn.commit()
    cursor.close()
    conn.close()


def get_twin(twin_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM twins WHERE id = %s", (twin_id,))
    row = cursor.fetchone()
    result = _row_to_dict(cursor, row)
    cursor.close()
    conn.close()
    return result


def create_conversation(conv_id: str, twin_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO conversations (id, twin_id) VALUES (%s, %s)", (conv_id, twin_id))
    conn.commit()
    cursor.close()
    conn.close()


def add_message(msg_id: str, conversation_id: str, role: str, content: str,
                sources: str = "[]", mood: str = "neutral", audio_path: str = None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (id, conversation_id, role, content, sources, mood, audio_path) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (msg_id, conversation_id, role, content, sources, mood, audio_path)
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_messages(conversation_id: str, limit: int = 50):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM messages WHERE conversation_id = %s ORDER BY created_at ASC LIMIT %s",
        (conversation_id, limit)
    )
    rows = cursor.fetchall()
    result = _rows_to_dicts(cursor, rows)
    cursor.close()
    conn.close()
    return result


def get_conversations_for_twin(twin_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM conversations WHERE twin_id = %s ORDER BY created_at DESC",
        (twin_id,)
    )
    rows = cursor.fetchall()
    result = _rows_to_dicts(cursor, rows)
    cursor.close()
    conn.close()
    return result


def create_onboarding_session(session_id: str, user_id: str, twin_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO onboarding_sessions (id, user_id, twin_id) VALUES (%s, %s, %s)",
        (session_id, user_id, twin_id)
    )
    conn.commit()
    cursor.close()
    conn.close()


def update_onboarding(session_id: str, **kwargs):
    conn = get_connection()
    cursor = conn.cursor()
    set_clause = ", ".join(f"{k} = %s" for k in kwargs.keys())
    values = list(kwargs.values()) + [session_id]
    cursor.execute(f"UPDATE onboarding_sessions SET {set_clause} WHERE id = %s", values)
    conn.commit()
    cursor.close()
    conn.close()


def get_onboarding(session_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM onboarding_sessions WHERE id = %s", (session_id,))
    row = cursor.fetchone()
    result = _row_to_dict(cursor, row)
    cursor.close()
    conn.close()
    return result

