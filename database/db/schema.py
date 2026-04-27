"""
ParkPredict — Database Schema
===============================
Creates all tables. Safe to call on every app startup (uses IF NOT EXISTS).

Tables:
  - parking_zones   : static + live info for each parking area
  - parking_logs    : every check-in / check-out event
"""

from db.connection import get_connection


def create_tables():
    """Create parking_zones and parking_logs tables if they don't exist."""

    conn = get_connection()
    cursor = conn.cursor()

    # ── TABLE 1: parking_zones ─────────────────────────────────────────────
    # Stores static info (name, location, capacity) and live slot count.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parking_zones (
            zone_id         INTEGER PRIMARY KEY AUTOINCREMENT,
            zone_name       TEXT    NOT NULL UNIQUE,
            location        TEXT    NOT NULL,
            total_slots     INTEGER NOT NULL CHECK(total_slots > 0),
            available_slots INTEGER NOT NULL CHECK(available_slots >= 0),
            status          TEXT    NOT NULL DEFAULT 'available'
                                CHECK(status IN ('available', 'full', 'maintenance')),
            last_updated    DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── TABLE 2: parking_logs ──────────────────────────────────────────────
    # One row per parking session. check_out_time is NULL while car is parked.
    # day_of_week and hour_of_day are stored at insert time for fast analytics.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parking_logs (
            log_id          INTEGER PRIMARY KEY AUTOINCREMENT,
            zone_id         INTEGER  NOT NULL,
            user_id         TEXT     NOT NULL,
            vehicle_plate   TEXT,
            check_in_time   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            check_out_time  DATETIME,
            duration_minutes INTEGER,
            day_of_week     TEXT     NOT NULL,
            hour_of_day     INTEGER  NOT NULL CHECK(hour_of_day BETWEEN 0 AND 23),
            FOREIGN KEY (zone_id) REFERENCES parking_zones(zone_id)
        )
    """)

    conn.commit()
    conn.close()
    print("[Schema] Tables ready.")
