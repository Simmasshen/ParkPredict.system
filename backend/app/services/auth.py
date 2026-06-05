"""
ParkPredict — Auth Service
============================
User management functions.
Creates a 'users' table in Nitesh's database for storing accounts.

Functions:
  create_users_table()         → creates users table (called on startup)
  create_user(...)             → insert new user
  find_user_by_username(...)   → lookup by username
  find_user_by_id(...)         → lookup by user_id
  hash_password(password)      → SHA-256 hash
  verify_password(plain, hash) → check password
"""

import hashlib
import os
from app.database import get_connection


# ── TABLE SETUP ───────────────────────────────────────────────────────────

def create_users_table():
    """
    Create the users table if it doesn't exist.
    Call this once on app startup alongside init_db().
    """
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id      INTEGER  PRIMARY KEY AUTOINCREMENT,
            username     TEXT     NOT NULL UNIQUE,
            password_hash TEXT    NOT NULL,
            student_id   TEXT,               -- links to parking_logs.user_id
            email        TEXT,
            created_at   DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


# ── PASSWORD HELPERS ──────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    """Hash a plain text password using SHA-256 + salt."""
    salt   = "parkpredict_mmu_2025"   # fixed salt for simplicity
    salted = plain + salt
    return hashlib.sha256(salted.encode()).hexdigest()


def verify_password(plain: str, stored_hash: str) -> bool:
    """Check if a plain text password matches the stored hash."""
    return hash_password(plain) == stored_hash


# ── USER CRUD ─────────────────────────────────────────────────────────────

def create_user(username: str, password_hash: str,
                student_id: str = "", email: str = "") -> int:
    """
    Insert a new user into the database.
    Returns the new user_id.
    """
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (username, password_hash, student_id, email)
        VALUES (?, ?, ?, ?)
    """, (username, password_hash, student_id or None, email or None))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id


def find_user_by_username(username: str) -> dict | None:
    """Return a user dict by username, or None if not found."""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, username, password_hash, student_id, email, created_at
        FROM   users
        WHERE  username = ?
    """, (username,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def find_user_by_id(user_id: int) -> dict | None:
    """Return a user dict by user_id, or None if not found."""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, username, password_hash, student_id, email, created_at
        FROM   users
        WHERE  user_id = ?
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None
