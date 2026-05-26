"""
ParkPredict — Database Schema
===============================
Creates all tables and indexes.
Safe to call on every app startup (uses IF NOT EXISTS).

Tables:
  - parking_zones   : static + live info for each parking area
  - parking_logs    : every check-in / check-out event

Indexes (for query performance):
  - idx_logs_zone_id       : speeds up queries filtering by zone
  - idx_logs_check_in_time : speeds up date-range analytics queries
  - idx_logs_user_id       : speeds up user history lookups
  - idx_logs_checkout_null : speeds up active session queries
  - idx_logs_day_hour      : speeds up peak hour GROUP BY queries
"""

from db.connection import get_connection


def create_tables():
    """Create parking_zones and parking_logs tables + indexes if they don't exist."""

    conn   = get_connection()
    cursor = conn.cursor()

    # ── TABLE 1: parking_zones ─────────────────────────────────────────────
    # Stores static info (name, location, capacity) and live slot count.
    # Normalization: zone info is separated from logs — no duplication.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parking_zones (
            zone_id         INTEGER PRIMARY KEY AUTOINCREMENT,
            zone_name       TEXT    NOT NULL UNIQUE,          -- UNIQUE enforces no duplicate zone names
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
    # Normalization: zone details stored once in parking_zones, referenced here by zone_id only.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parking_logs (
            log_id           INTEGER PRIMARY KEY AUTOINCREMENT,
            zone_id          INTEGER  NOT NULL,
            user_id          TEXT     NOT NULL,
            vehicle_plate    TEXT,
            check_in_time    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            check_out_time   DATETIME,                        -- NULL = still parked
            duration_minutes INTEGER,                         -- calculated on check-out
            day_of_week      TEXT     NOT NULL,               -- stored at insert for fast GROUP BY
            hour_of_day      INTEGER  NOT NULL CHECK(hour_of_day BETWEEN 0 AND 23),
            FOREIGN KEY (zone_id) REFERENCES parking_zones(zone_id)  -- enforces referential integrity
        )
    """)

    # ── INDEXES ───────────────────────────────────────────────────────────
    # Indexes speed up SELECT queries that filter or sort by these columns.
    # Without indexes, SQLite scans every row — slow when data grows large.

    # 1. Speed up: get_active_logs(zone_id) — filters by zone_id
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_logs_zone_id
        ON parking_logs(zone_id)
    """)

    # 2. Speed up: get_peak_hours() — filters by check_in_time date range
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_logs_check_in_time
        ON parking_logs(check_in_time)
    """)

    # 3. Speed up: get_logs_by_user() — filters by user_id
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_logs_user_id
        ON parking_logs(user_id)
    """)

    # 4. Speed up: get_active_logs() — filters WHERE check_out_time IS NULL
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_logs_checkout_null
        ON parking_logs(check_out_time)
    """)

    # 5. Speed up: get_peak_hours() & get_prediction_data() — GROUP BY day/hour
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_logs_day_hour
        ON parking_logs(day_of_week, hour_of_day)
    """)

    conn.commit()
    conn.close()
    print("[Schema] Tables and indexes ready.")
