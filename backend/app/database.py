"""
ParkPredict — Database Bridge (Pirai → Nitesh's Database Project)
=================================================================
This file connects Pirai's Flask backend to Nitesh's database project.

TEAM ALLOCATION:
    Pirai       → Backend development (Flask API, routes, services)
    Nitesh      → Database layer (SQLite, schema, operations, queries)
    Bala        → Frontend development (UI components)

REQUIRED FOLDER STRUCTURE:
    parkpredict/                  ← shared parent folder
    ├── backend/                  ← Pirai's project (this folder)
    │   ├── app.py
    │   ├── requirements.txt
    │   └── app/
    │       ├── __init__.py
    │       ├── database.py       ← THIS FILE
    │       ├── routes/
    │       └── services/
    └── database/                 ← Nitesh's project (MUST be named 'database')
        └── db/
            ├── __init__.py
            ├── schema.py         → create_tables()
            ├── seed.py           → seed_zones()
            ├── operations.py     → check_in(), check_out()
            ├── queries.py        → get_all_zones(), get_zone_by_id(), 
            │                       get_active_logs(), get_logs_by_user(),
            │                       get_daily_stats(), get_peak_hours(), 
            │                       get_prediction_data()
            ├── admin.py          → update_zone_status(), reset_zone_slots(),
            │                       get_admin_logs(), get_capacity_history()
            └── parkpredict.db    ← Nitesh's SQLite database file

HOW TO SET UP (First Time):
    1. Create shared folder: C:/Users/pirai/Desktop/parkpredict/
    2. Clone/place Pirai's backend inside: parkpredict/backend/
    3. Clone/place Nitesh's database inside: parkpredict/database/
    4. Run from backend folder:
           cd parkpredict/backend
           python app.py

CONNECTION FLOW:
    Flask routes → Pirai's services → This bridge (database.py)
                                    ↓
                          Nitesh's database project
                          (db/operations, db/queries, etc.)
"""

import sys
import os
import sqlite3

# ────────────────────────────────────────────────────────────────────────────
# EXPORTED FUNCTIONS (for use across the Flask app)
# ────────────────────────────────────────────────────────────────────────────
__all__ = [
    # Initialization
    "init_db",
    "get_connection",
    
    # Nitesh's schema & seeding
    "create_tables",
    "seed_zones",
    
    # Nitesh's operations (check-in/check-out)
    "check_in",
    "check_out",
    
    # Nitesh's queries (read operations)
    "get_all_zones",
    "get_zone_by_id",
    "get_active_logs",
    "get_logs_by_user",
    "get_daily_stats",
    "get_peak_hours",
    "get_prediction_data",
    
    # Nitesh's admin functions
    "update_zone_status",
    "reset_zone_slots",
    "get_admin_logs",
    "get_capacity_history",
]

# ────────────────────────────────────────────────────────────────────────────
# LOCATE NITESH'S DATABASE PROJECT
# ────────────────────────────────────────────────────────────────────────────
# Navigation: this file (database.py)
#            → app/ folder
#            → backend/ folder
#            → parkpredict/ (parent)
#            → then into database/ (Nitesh's project)

DB_PROJECT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "database")
DB_PROJECT_PATH = os.path.normpath(DB_PROJECT_PATH)

# ────────────────────────────────────────────────────────────────────────────
# ERROR HANDLING: Friendly messages if Nitesh's folder is missing
# ────────────────────────────────────────────────────────────────────────────
if not os.path.isdir(DB_PROJECT_PATH):
    raise FileNotFoundError(
        f"\n\n[ParkPredict Bridge] ❌ Cannot find Nitesh's 'database' folder.\n"
        f"Expected it at: {DB_PROJECT_PATH}\n\n"
        f"Make sure folder structure looks like this:\n"
        f"  parkpredict/\n"
        f"  ├── backend/    ← Pirai's Flask app (you are here)\n"
        f"  └── database/   ← Nitesh's database project (MUST be named 'database')\n\n"
        f"Contact: Make sure Nitesh has set up his 'database/' folder.\n"
    )

if not os.path.isdir(os.path.join(DB_PROJECT_PATH, "db")):
    raise FileNotFoundError(
        f"\n\n[ParkPredict Bridge] ❌ Found Nitesh's 'database' folder, "
        f"but no 'db/' subfolder inside.\n"
        f"Expected: {DB_PROJECT_PATH}/db/\n\n"
        f"Nitesh needs to create a 'db/' package inside his 'database/' folder:\n"
        f"  database/\n"
        f"  └── db/\n"
        f"      ├── __init__.py\n"
        f"      ├── schema.py\n"
        f"      ├── seed.py\n"
        f"      ├── operations.py\n"
        f"      ├── queries.py\n"
        f"      └── admin.py\n"
    )

# ────────────────────────────────────────────────────────────────────────────
# ADD NITESH'S FOLDER TO PYTHON PATH (so we can import from db/)
# ────────────────────────────────────────────────────────────────────────────
if DB_PROJECT_PATH not in sys.path:
    sys.path.insert(0, DB_PROJECT_PATH)
    print(f"[ParkPredict Bridge] Added Nitesh's database project to Python path: {DB_PROJECT_PATH}")

# ────────────────────────────────────────────────────────────────────────────
# IMPORT NITESH'S FUNCTIONS FROM HIS DATABASE PROJECT
# ────────────────────────────────────────────────────────────────────────────
try:
    # Schema and initialization (from Nitesh's schema.py)
    from db.schema import create_tables
    
    # Seeding default data (from Nitesh's seed.py)
    from db.seed import seed_zones
    
    # Check-in/check-out operations (from Nitesh's operations.py)
    from db.operations import check_in, check_out
    
    # Query functions for dashboard & analytics (from Nitesh's queries.py)
    from db.queries import (
        get_all_zones,
        get_zone_by_id,
        get_active_logs,
        get_logs_by_user,
        get_daily_stats,
        get_peak_hours,
        get_prediction_data,
    )
    
    # Admin management functions (from Nitesh's admin.py)
    from db.admin import (
        update_zone_status,
        reset_zone_slots,
        get_admin_logs,
        get_capacity_history,
    )

except ImportError as e:
    raise ImportError(
        f"\n\n[ParkPredict Bridge] ❌ Connected to Nitesh's database folder, "
        f"but a required function is MISSING.\n"
        f"Error: {e}\n\n"
        f"Nitesh's db/ package must have these files:\n"
        f"  ✓ db/schema.py     → must export: create_tables()\n"
        f"  ✓ db/seed.py       → must export: seed_zones()\n"
        f"  ✓ db/operations.py → must export: check_in(), check_out()\n"
        f"  ✓ db/queries.py    → must export: get_all_zones(), get_zone_by_id(),\n"
        f"                                     get_active_logs(), get_logs_by_user(),\n"
        f"                                     get_daily_stats(), get_peak_hours(),\n"
        f"                                     get_prediction_data()\n"
        f"  ✓ db/admin.py      → must export: update_zone_status(), reset_zone_slots(),\n"
        f"                                     get_admin_logs(), get_capacity_history()\n\n"
        f"Contact Nitesh to check his implementation.\n"
    )


# ────────────────────────────────────────────────────────────────────────────
# INITIALIZATION: Called once when Flask app starts
# ────────────────────────────────────────────────────────────────────────────
def init_db():
    """
    Initialize the database on Flask app startup.
    
    This function:
    1. Calls Nitesh's create_tables() to set up schema
    2. Calls Nitesh's seed_zones() to populate default zones
    3. Confirms connection is ready
    
    Should be called in Flask app.__init__.py during app creation.
    
    Example:
        from app.database import init_db
        
        app = Flask(__name__)
        init_db()  # Set up Nitesh's database
    """
    create_tables()
    seed_zones()
    print("[ParkPredict] ✓ Connected to Nitesh's database successfully.")
    print("[ParkPredict] ✓ Database tables created and seeded.")
    print("[ParkPredict] ✓ Ready for operations.")


# ────────────────────────────────────────────────────────────────────────────
# DATABASE CONNECTION: Access Nitesh's shared parkpredict.db
# ────────────────────────────────────────────────────────────────────────────
def get_connection():
    """
    Return a SQLite connection to Nitesh's shared parkpredict.db.
    
    This connection is used by:
    - Pirai's auth service (user login/registration)
    - Pirai's business logic (calling Nitesh's functions)
    
    Database Location: database/parkpredict.db (Nitesh's project)
    
    Features:
    - row_factory set to sqlite3.Row (access rows like dicts)
    - Foreign key constraints enabled (data integrity)
    - check_same_thread=False (safe for Flask's threading)
    
    Returns:
        sqlite3.Connection — connected to parkpredict.db
        
    Example:
        from app.database import get_connection
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        conn.close()
    """
    db_path = os.path.join(DB_PROJECT_PATH, "parkpredict.db")
    
    # Create connection
    conn = sqlite3.connect(db_path, check_same_thread=False)
    
    # Allow accessing columns by name (dict-like behavior)
    conn.row_factory = sqlite3.Row
    
    # Enforce foreign key constraints for data integrity
    conn.execute("PRAGMA foreign_keys = ON")
    
    return conn
