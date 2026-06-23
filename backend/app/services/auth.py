"""
ParkPredict — Auth Service
User management functions using the shared parkpredict.db.
"""

import hashlib
from app.database import get_connection


def create_users_table():
    """Create users table if it doesn't exist. Called on app startup."""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id       INTEGER  PRIMARY KEY AUTOINCREMENT,
            username      TEXT     NOT NULL UNIQUE,
            password_hash TEXT     NOT NULL,
            student_id    TEXT,
            email         TEXT,
            role          TEXT     NOT NULL DEFAULT 'user'
                              CHECK(role IN ('user', 'admin')),
            created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def hash_password(plain: str) -> str:
    """Hash a plain text password using SHA-256 + salt."""
    salt   = "parkpredict_mmu_2025"
    return hashlib.sha256((plain + salt).encode()).hexdigest()


def verify_password(plain: str, stored_hash: str) -> bool:
    """Check if a plain text password matches the stored hash."""
    return hash_password(plain) == stored_hash


def create_user(username: str, password_hash: str,
                student_id: str = "", email: str = "", role: str = "user") -> int:
    """Insert a new user. Returns new user_id."""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (username, password_hash, student_id, email, role)
        VALUES (?, ?, ?, ?, ?)
    """, (username, password_hash, student_id or None, email or None, role))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id


def find_user_by_username(username: str) -> dict | None:
    """Return a user dict by username, or None."""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, username, password_hash, student_id, email, role, created_at
        FROM   users WHERE username = ?
    """, (username,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def find_user_by_id(user_id: int) -> dict | None:
    """Return a user dict by user_id, or None."""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, username, password_hash, student_id, email, role, created_at
        FROM   users WHERE user_id = ?
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None
