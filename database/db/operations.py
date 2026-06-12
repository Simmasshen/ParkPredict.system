"""
ParkPredict — Parking Operations
==================================
Handles all check-in and check-out logic.
Now records capacity history on every transaction.

Functions:
  check_in(zone_id, user_id, vehicle_plate)  → insert log + update zone
  check_out(log_id)                          → update log + restore slot
"""

from datetime import datetime
from db.connection import get_connection


def _record_capacity(cursor, zone_id: int):
    """
    Snapshot the current slot count into zone_capacity_history.
    Called after every check-in and check-out.
    Used by Bala's real-time chart and admin dashboard.
    """
    cursor.execute("""
        INSERT INTO zone_capacity_history (zone_id, available_slots, total_slots)
        SELECT zone_id, available_slots, total_slots
        FROM   parking_zones
        WHERE  zone_id = ?
    """, (zone_id,))


def check_in(zone_id: int, user_id: str, vehicle_plate: str = None) -> dict:
    """
    Record a user checking in to a parking zone.

    Steps:
      1. Verify zone exists and has available slots.
      2. Block double check-in — same user can't park twice.
      3. Insert a new row in parking_logs.
      4. Decrement available_slots; mark zone 'full' if needed.
      5. Record capacity snapshot for real-time chart.

    Returns:
      dict { success, log_id, zone_name, check_in, slots_left }
      or   { success: False, error: "..." }
    """
    now         = datetime.now()
    day_of_week = now.strftime("%A")
    hour_of_day = now.hour

    conn   = get_connection()
    cursor = conn.cursor()

    try:
        # 1. Validate zone
        cursor.execute("""
            SELECT zone_id, zone_name, available_slots, status
            FROM   parking_zones WHERE zone_id = ?
        """, (zone_id,))
        zone = cursor.fetchone()

        if not zone:
            return {"success": False, "error": f"Zone {zone_id} not found."}
        if zone["available_slots"] <= 0 or zone["status"] == "full":
            return {"success": False, "error": f"{zone['zone_name']} is currently full."}
        if zone["status"] == "maintenance":
            return {"success": False, "error": f"{zone['zone_name']} is under maintenance."}

        # 2. Block double check-in
        cursor.execute("""
            SELECT log_id FROM parking_logs
            WHERE  user_id = ? AND check_out_time IS NULL
        """, (user_id,))
        if cursor.fetchone():
            return {"success": False,
                    "error": "You already have an active parking session. Please check out first."}

        # 3. Insert log
        cursor.execute("""
            INSERT INTO parking_logs
                (zone_id, user_id, vehicle_plate, check_in_time, day_of_week, hour_of_day)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (zone_id, user_id, vehicle_plate,
              now.strftime("%Y-%m-%d %H:%M:%S"), day_of_week, hour_of_day))

        log_id = cursor.lastrowid

        # 4. Update zone
        new_slots  = zone["available_slots"] - 1
        new_status = "full" if new_slots == 0 else "available"

        cursor.execute("""
            UPDATE parking_zones
            SET    available_slots = ?, status = ?, last_updated = CURRENT_TIMESTAMP
            WHERE  zone_id = ?
        """, (new_slots, new_status, zone_id))

        # 5. Record capacity snapshot for real-time chart
        _record_capacity(cursor, zone_id)

        conn.commit()
        return {
            "success":    True,
            "log_id":     log_id,
            "zone_name":  zone["zone_name"],
            "check_in":   now.strftime("%Y-%m-%d %H:%M:%S"),
            "slots_left": new_slots,
        }

    except Exception as e:
        conn.rollback()
        return {"success": False, "error": str(e)}

    finally:
        conn.close()


def check_out(log_id: int) -> dict:
    """
    Record a user checking out from a parking zone.

    Steps:
      1. Fetch the open log (check_out_time IS NULL).
      2. Calculate parking duration in minutes.
      3. Update log with check-out time and duration.
      4. Increment available_slots in parking_zones.
      5. Record capacity snapshot for real-time chart.

    Returns:
      dict { success, log_id, zone_name, check_out, duration_minutes }
      or   { success: False, error: "..." }
    """
    now = datetime.now()

    conn   = get_connection()
    cursor = conn.cursor()

    try:
        # 1. Fetch open log
        cursor.execute("""
            SELECT pl.log_id, pl.zone_id, pl.check_in_time, pz.zone_name
            FROM   parking_logs pl
            JOIN   parking_zones pz ON pl.zone_id = pz.zone_id
            WHERE  pl.log_id = ? AND pl.check_out_time IS NULL
        """, (log_id,))
        log = cursor.fetchone()

        if not log:
            return {"success": False,
                    "error": f"No active check-in found for log_id {log_id}."}

        # 2. Calculate duration
        check_in_dt      = datetime.strptime(log["check_in_time"], "%Y-%m-%d %H:%M:%S")
        duration_minutes = int((now - check_in_dt).total_seconds() / 60)

        # 3. Update log
        cursor.execute("""
            UPDATE parking_logs
            SET    check_out_time = ?, duration_minutes = ?
            WHERE  log_id = ?
        """, (now.strftime("%Y-%m-%d %H:%M:%S"), duration_minutes, log_id))

        # 4. Restore slot
        cursor.execute("""
            UPDATE parking_zones
            SET    available_slots = available_slots + 1,
                   status          = 'available',
                   last_updated    = CURRENT_TIMESTAMP
            WHERE  zone_id = ?
        """, (log["zone_id"],))

        # 5. Record capacity snapshot
        _record_capacity(cursor, log["zone_id"])

        conn.commit()
        return {
            "success":          True,
            "log_id":           log_id,
            "zone_name":        log["zone_name"],
            "check_out":        now.strftime("%Y-%m-%d %H:%M:%S"),
            "duration_minutes": duration_minutes,
        }

    except Exception as e:
        conn.rollback()
        return {"success": False, "error": str(e)}

    finally:
        conn.close()
