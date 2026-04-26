"""
ParkPredict — Queries
======================
All SELECT queries for retrieving parking data.

Functions:
  get_all_zones()           → live status of all zones (for Bala's map)
  get_zone_by_id(zone_id)   → single zone status
  get_active_logs(zone_id)  → currently-parked vehicles
  get_logs_by_user(user_id) → parking history for a user
  get_peak_hours(days)      → check-in counts by day/hour (for charts)
  get_prediction_data()     → avg occupancy per zone/day/hour (for Pirai)
"""

from db.connection import get_connection


# ── ZONE STATUS ────────────────────────────────────────────────────────────

def get_all_zones() -> list:
    """
    Return live status of every parking zone.
    Used by Bala (Frontend) to colour zones green / red on the map.
    """
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT zone_id, zone_name, location,
               total_slots, available_slots, status, last_updated
        FROM   parking_zones
        ORDER  BY zone_id
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_zone_by_id(zone_id: int) -> dict | None:
    """Return a single zone's live status, or None if not found."""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT zone_id, zone_name, location,
               total_slots, available_slots, status, last_updated
        FROM   parking_zones
        WHERE  zone_id = ?
    """, (zone_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


# ── ACTIVE SESSIONS ────────────────────────────────────────────────────────

def get_active_logs(zone_id: int = None) -> list:
    """
    Return all currently-parked vehicles (check_out_time IS NULL).

    Args:
      zone_id: optional filter — if None, returns all zones.
    """
    conn   = get_connection()
    cursor = conn.cursor()

    if zone_id:
        cursor.execute("""
            SELECT log_id, zone_id, user_id, vehicle_plate,
                   check_in_time, day_of_week, hour_of_day
            FROM   parking_logs
            WHERE  check_out_time IS NULL AND zone_id = ?
            ORDER  BY check_in_time DESC
        """, (zone_id,))
    else:
        cursor.execute("""
            SELECT log_id, zone_id, user_id, vehicle_plate,
                   check_in_time, day_of_week, hour_of_day
            FROM   parking_logs
            WHERE  check_out_time IS NULL
            ORDER  BY check_in_time DESC
        """)

    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


# ── USER HISTORY ───────────────────────────────────────────────────────────

def get_logs_by_user(user_id: str, limit: int = 20) -> list:
    """Return recent parking history for a specific user (newest first)."""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT log_id, zone_id, vehicle_plate,
               check_in_time, check_out_time, duration_minutes
        FROM   parking_logs
        WHERE  user_id = ?
        ORDER  BY check_in_time DESC
        LIMIT  ?
    """, (user_id, limit))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


# ── ANALYTICS ─────────────────────────────────────────────────────────────

def get_peak_hours(days: int = 30) -> list:
    """
    Return check-in counts grouped by zone, day of week, and hour.
    Pirai feeds this into Pandas to generate peak-hour bar charts.

    Args:
      days: how many past days to include (default: 30)

    Returns:
      List of dicts: zone_id, day_of_week, hour_of_day, total_checkins
    """
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT   zone_id,
                 day_of_week,
                 hour_of_day,
                 COUNT(*) AS total_checkins
        FROM     parking_logs
        WHERE    check_in_time >= datetime('now', ?)
        GROUP BY zone_id, day_of_week, hour_of_day
        ORDER BY zone_id, day_of_week, hour_of_day
    """, (f"-{days} days",))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_prediction_data() -> list:
    """
    Return average occupancy per zone / day / hour.
    Clean, aggregated — ready for Pirai's Pandas prediction model.

    Returns:
      List of dicts:
        zone_id, day_of_week, hour_of_day,
        total_entries, avg_duration_min, avg_entries_per_day
    """
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            p1.zone_id,
            p1.day_of_week,
            p1.hour_of_day,
            COUNT(*)                        AS total_entries,
            ROUND(AVG(p1.duration_minutes), 1)
                                            AS avg_duration_min,
            ROUND(
                COUNT(*) * 1.0 /
                NULLIF((
                    SELECT COUNT(DISTINCT date(p2.check_in_time))
                    FROM   parking_logs p2
                    WHERE  p2.zone_id = p1.zone_id
                ), 0),
                2
            )                               AS avg_entries_per_day
        FROM     parking_logs p1
        WHERE    p1.check_out_time IS NOT NULL
        GROUP BY p1.zone_id, p1.day_of_week, p1.hour_of_day
        ORDER BY p1.zone_id, p1.day_of_week, p1.hour_of_day
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows
