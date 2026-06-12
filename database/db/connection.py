"""
ParkPredict — Database Connection
===================================
Provides a single get_connection() function used by all other modules.
"""

import sqlite3
from db.config import DB_PATH


def get_connection() -> sqlite3.Connection:
    """
    Return a SQLite connection with:
      - row_factory = sqlite3.Row  (access columns by name, like a dict)
      - foreign key enforcement ON
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn