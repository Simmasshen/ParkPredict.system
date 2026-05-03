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
  get_daily_stats(date)     → daily statistics for dashboard
"""

from datetime import datetime
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


# ── DAILY STATISTICS ───────────────────────────────────────────────────────

def get_daily_stats(date: str = None) -> dict:
    """
    Return daily statistics for the dashboard.

    Args:
      date: target date as 'YYYY-MM-DD' string.
            Defaults to today if not provided.

    Returns:
      dict with:
        date, total_checkins, total_checkouts,
        currently_parked, avg_duration_minutes,
        busiest_zone, zone_usage_today
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    conn   = get_connection()
    cursor = conn.cursor()

    # Total check-ins today
    cursor.execute("""
        SELECT COUNT(*) AS total_checkins
        FROM   parking_logs
        WHERE  date(check_in_time) = ?
    """, (date,))
    total_checkins = cursor.fetchone()["total_checkins"]

    # Total check-outs today
    cursor.execute("""
        SELECT COUNT(*) AS total_checkouts
        FROM   parking_logs
        WHERE  date(check_out_time) = ?
    """, (date,))
    total_checkouts = cursor.fetchone()["total_checkouts"]

    # Currently parked right now (no check-out yet)
    cursor.execute("""
        SELECT COUNT(*) AS currently_parked
        FROM   parking_logs
        WHERE  check_out_time IS NULL
    """)
    currently_parked = cursor.fetchone()["currently_parked"]

    # Average parking duration today (completed sessions only)
    cursor.execute("""
        SELECT ROUND(AVG(duration_minutes), 1) AS avg_duration
        FROM   parking_logs
        WHERE  date(check_in_time) = ?
          AND  check_out_time IS NOT NULL
    """, (date,))
    avg_duration = cursor.fetchone()["avg_duration"] or 0

    # Busiest zone today (most check-ins)
    cursor.execute("""
        SELECT   pz.zone_name, COUNT(*) AS total
        FROM     parking_logs pl
        JOIN     parking_zones pz ON pl.zone_id = pz.zone_id
        WHERE    date(pl.check_in_time) = ?
        GROUP BY pl.zone_id
        ORDER BY total DESC
        LIMIT    1
    """, (date,))
    row = cursor.fetchone()
    busiest_zone = row["zone_name"] if row else "No data"

    # Per-zone usage breakdown for today
    cursor.execute("""
        SELECT   pz.zone_name,
                 COUNT(pl.log_id)               AS checkins_today,
                 pz.available_slots,
                 pz.total_slots
        FROM     parking_zones pz
        LEFT JOIN parking_logs pl
               ON pz.zone_id = pl.zone_id
              AND date(pl.check_in_time) = ?
        GROUP BY pz.zone_id
        ORDER BY pz.zone_id
    """, (date,))
    zone_usage_today = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return {
        "date":                 date,
        "total_checkins":       total_checkins,
        "total_checkouts":      total_checkouts,
        "currently_parked":     currently_parked,
        "avg_duration_minutes": avg_duration,
        "busiest_zone":         busiest_zone,
        "zone_usage_today":     zone_usage_today,
    }

