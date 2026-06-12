"""
ParkPredict — Database Schema
===============================
Creates all tables and indexes.
Safe to call on every app startup (uses IF NOT EXISTS).

Tables:
  - parking_zones    : static + live info for each parking area
  - parking_logs     : every check-in / check-out event
  - admin_logs       : every admin action (audit trail)
  - zone_capacity_history : history of slot changes over time

Indexes:
  - idx_logs_zone_id, check_in_time, user_id, checkout_null, day_hour
  - idx_admin_zone_id, admin_logs_time
  - idx_capacity_zone_id
"""

from db.connection import get_connection


def create_tables():
    """Create all tables and indexes if they don't exist."""

    conn   = get_connection()
    cursor = conn.cursor()

    # ── TABLE 1: parking_zones ─────────────────────────────────────────────
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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parking_logs (
            log_id           INTEGER PRIMARY KEY AUTOINCREMENT,
            zone_id          INTEGER  NOT NULL,
            user_id          TEXT     NOT NULL,
            vehicle_plate    TEXT,
            check_in_time    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            check_out_time   DATETIME,
            duration_minutes INTEGER,
            day_of_week      TEXT     NOT NULL,
            hour_of_day      INTEGER  NOT NULL CHECK(hour_of_day BETWEEN 0 AND 23),
            FOREIGN KEY (zone_id) REFERENCES parking_zones(zone_id)
        )
    """)

    # ── TABLE 3: admin_logs ────────────────────────────────────────────────
    # Audit trail — every admin action is recorded.
    # Pirai uses GET /api/admin/audit to show this on the admin page.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_logs (
            action_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            zone_id      INTEGER,
            action       TEXT    NOT NULL,
            old_value    TEXT,
            new_value    TEXT,
            performed_by TEXT    NOT NULL DEFAULT 'admin',
            action_time  DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (zone_id) REFERENCES parking_zones(zone_id)
        )
    """)

    # ── TABLE 4: zone_capacity_history ─────────────────────────────────────
    # Tracks slot count over time — used for occupancy trend charts.
    # Recorded every time check-in or check-out happens.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS zone_capacity_history (
            history_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            zone_id         INTEGER NOT NULL,
            available_slots INTEGER NOT NULL,
            total_slots     INTEGER NOT NULL,
            recorded_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (zone_id) REFERENCES parking_zones(zone_id)
        )
    """)

    # ── INDEXES ───────────────────────────────────────────────────────────

    # parking_logs indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_zone_id        ON parking_logs(zone_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_check_in_time  ON parking_logs(check_in_time)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_user_id        ON parking_logs(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_checkout_null  ON parking_logs(check_out_time)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_day_hour       ON parking_logs(day_of_week, hour_of_day)")

    # admin_logs indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_admin_zone_id   ON admin_logs(zone_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_admin_logs_time ON admin_logs(action_time)")

    # zone_capacity_history indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_capacity_zone_id   ON zone_capacity_history(zone_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_capacity_recorded  ON zone_capacity_history(recorded_at)")

    conn.commit()
    conn.close()
    print("[Schema] Tables and indexes ready.")