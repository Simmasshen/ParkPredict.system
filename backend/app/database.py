"""
ParkPredict — Database Bridge (Pirai → Nitesh)
================================================
This file connects Pirai's Flask backend to Nitesh's database project.

REQUIRED FOLDER STRUCTURE:
    parkpredict/                  ← shared parent folder (any name is fine)
    ├── backend/                  ← Pirai's project  (this folder)
    │   ├── app.py
    │   ├── requirements.txt
    │   └── app/
    │       ├── __init__.py
    │       ├── database.py       ← this file
    │       ├── routes/
    │       └── services/
    └── database/                 ← Nitesh's project (must be named 'database')
        └── db/
            ├── schema.py         ← must have: create_tables()
            ├── seed.py           ← must have: seed_zones()
            ├── operations.py     ← must have: check_in(), check_out()
            ├── queries.py        ← must have: get_all_zones(), get_zone_by_id(),
            │                                  get_active_logs(), get_logs_by_user(),
            │                                  get_peak_hours(), get_prediction_data()
            └── admin.py          ← must have: update_zone_status(), reset_zone_slots()

HOW TO SET UP (both Pirai and Nitesh do this once):
    1. Create a shared folder, e.g. C:/Users/pirai/Desktop/parkpredict/
    2. Put Pirai's backend folder inside it   → parkpredict/backend/
    3. Put Nitesh's database folder inside it → parkpredict/database/
    4. Run from inside the backend folder:
           cd parkpredict/backend
           python app.py
"""

import sys
import os

# ── Locate Nitesh's database folder ───────────────────────────────────────
# Goes up: database.py → app/ → backend/ → parkpredict/ → then into database/
DB_PROJECT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "database")
DB_PROJECT_PATH = os.path.normpath(DB_PROJECT_PATH)

# ── Friendly error if Nitesh's folder is missing ──────────────────────────
if not os.path.isdir(DB_PROJECT_PATH):
    raise FileNotFoundError(
        f"\n\n[ParkPredict] Cannot find Nitesh's database folder.\n"
        f"Expected it at: {DB_PROJECT_PATH}\n\n"
        f"Make sure your folder structure looks like this:\n"
        f"  parkpredict/\n"
        f"  ├── backend/    ← you are here\n"
        f"  └── database/   ← Nitesh's project (folder must be named 'database')\n"
    )

if not os.path.isdir(os.path.join(DB_PROJECT_PATH, "db")):
    raise FileNotFoundError(
        f"\n\n[ParkPredict] Found Nitesh's database folder but no 'db/' subfolder inside it.\n"
        f"Expected: {DB_PROJECT_PATH}/db/\n"
        f"Tell Nitesh his db/ package must be directly inside the 'database/' folder.\n"
    )

# ── Add Nitesh's folder to Python path so we can import from it ───────────
if DB_PROJECT_PATH not in sys.path:
    sys.path.insert(0, DB_PROJECT_PATH)

# ── Import Nitesh's functions ──────────────────────────────────────────────
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
    from db.admin import update_zone_status, reset_zone_slots

    # Expose it as 'get_connection' so auth.py can find it
    get_connection = get_db_connection

except ImportError as e:
    raise ImportError(
        f"\n\n[ParkPredict] Connected to Nitesh's database folder but a required "
        f"function is missing.\n"
        f"Missing: {e}\n\n"
        f"Send this message to Nitesh — his db/ package must export:\n"
        f"  db/schema.py     → create_tables()\n"
        f"  db/seed.py       → seed_zones()\n"
        f"  db/operations.py → check_in(), check_out()\n"
        f"  db/queries.py    → get_all_zones(), get_zone_by_id(), get_active_logs(),\n"
        f"                     get_logs_by_user(), get_peak_hours(), get_prediction_data()\n"
        f"  db/admin.py      → update_zone_status(), reset_zone_slots()\n"
    )


def init_db():
    """Call once on app startup to create tables and seed default data."""
    create_tables()
    seed_zones()
    print("[DB] Connected to Nitesh's database. Ready.")
