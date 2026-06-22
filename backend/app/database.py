"""
ParkPredict — Database Bridge
Connects the Flask backend to the database project.

REQUIRED FOLDER STRUCTURE:
    parkpredict/
    ├── backend/           ← Flask app
    │   ├── app.py
    │   └── app/
    │       └── database.py  ← this file
    └── database/          ← Database project (must be named 'database')
        └── db/
            ├── schema.py, seed.py, operations.py, queries.py, admin.py
"""

import sys
import os
import sqlite3

__all__ = [
    "init_db", "get_connection",
    "create_tables", "seed_zones",
    "check_in", "check_out",
    "get_all_zones", "get_zone_by_id",
    "get_active_logs", "get_logs_by_user",
    "get_daily_stats", "get_peak_hours",
    "get_prediction_data",
    "update_zone_status", "reset_zone_slots",
    "get_admin_logs", "get_capacity_history",
]

# ── Locate database folder ──────────────────────────────────────────────
# Goes up: database.py → app/ → backend/ → project root/ → database/
DB_PROJECT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "database")
DB_PROJECT_PATH = os.path.normpath(DB_PROJECT_PATH)

if not os.path.isdir(DB_PROJECT_PATH):
    raise FileNotFoundError(
        f"\n\n[ParkPredict] Cannot find 'database' folder.\n"
        f"Expected it at: {DB_PROJECT_PATH}\n\n"
        f"Folder structure must be:\n"
        f"  parkpredict/\n"
        f"  ├── backend/    ← you are here\n"
        f"  └── database/   ← database project\n"
    )

if DB_PROJECT_PATH not in sys.path:
    sys.path.insert(0, DB_PROJECT_PATH)

# ── Import database functions ──────────────────────────────────────────
try:
    from db.schema     import create_tables
    from db.seed       import seed_zones
    from db.operations import check_in, check_out
    from db.queries    import (
        get_all_zones,
        get_zone_by_id,
        get_active_logs,
        get_logs_by_user,
        get_daily_stats,
        get_peak_hours,
        get_prediction_data,
    )
    from db.admin import (
        update_zone_status,
        reset_zone_slots,
        get_admin_logs,
        get_capacity_history,
    )
except ImportError as e:
    raise ImportError(
        f"\n\n[ParkPredict] Missing function in database project: {e}\n"
    )


def init_db():
    """Call once on app startup to create tables and seed data."""
    create_tables()
    seed_zones()
    print("[DB] Database initialised and ready.")


# ── Shared SQLite connection for the same DB ───────────────────────────
def get_connection():
    """
    Return a SQLite connection to the shared parkpredict.db.
    Used by auth service to store user accounts in the same database.
    """
    # Database is stored inside database/parkpredict.db
    db_path = os.path.join(DB_PROJECT_PATH, "parkpredict.db")
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
