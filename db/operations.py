"""
ParkPredict — Parking Operations
==================================
Handles all check-in and check-out logic.

Functions:
  check_in(zone_id, user_id, vehicle_plate)  → insert log + update zone
  check_out(log_id)                          → update log + restore slot
"""

from datetime import datetime
from db.connection import get_connection


def check_in(zone_id: int, user_id: str, vehicle_plate: str = None) -> dict:
    """
    Record a user checking in to a parking zone.

    Steps:
      1. Verify the zone exists and has available slots.
      2. Insert a new row in parking_logs.
      3. Decrement available_slots; mark zone 'full' if needed.

    Returns:
      dict { success, log_id, zone_name, check_in, slots_left }
      or   { success: False, error: "..." }
    """
    now         = datetime.now()
    day_of_week = now.strftime("%A")   # e.g. 'Monday'
    hour_of_day = now.hour             # 0–23

    conn   = get_connection()
    cursor = conn.cursor()

    try:
        # 1. Validate zone
        cursor.execute("""
            SELECT zone_id, zone_name, available_slots, status
            FROM   parking_zones
            WHERE  zone_id = ?
        """, (zone_id,))
        zone = cursor.fetchone()

        if not zone:
            return {"success": False, "error": f"Zone {zone_id} not found."}
        if zone["available_slots"] <= 0 or zone["status"] == "full":
            return {"success": False, "error": f"{zone['zone_name']} is currently full."}
        if zone["status"] == "maintenance":
            return {"success": False, "error": f"{zone['zone_name']} is under maintenance."}

        # 2. Insert log
        cursor.execute("""
            INSERT INTO parking_logs
                (zone_id, user_id, vehicle_plate, check_in_time, day_of_week, hour_of_day)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (zone_id, user_id, vehicle_plate,
              now.strftime("%Y-%m-%d %H:%M:%S"), day_of_week, hour_of_day))

        log_id = cursor.lastrowid

        # 3. Update zone
        new_slots  = zone["available_slots"] - 1
        new_status = "full" if new_slots == 0 else "available"

        cursor.execute("""
            UPDATE parking_zones
            SET    available_slots = ?,
                   status          = ?,
                   last_updated    = CURRENT_TIMESTAMP
            WHERE  zone_id = ?
        """, (new_slots, new_status, zone_id))

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
      3. Update the log with check-out time and duration.
      4. Increment available_slots in parking_zones.

    Returns:
      dict { success, log_id, check_out, duration_minutes }
      or   { success: False, error: "..." }
    """
    now = datetime.now()

    conn   = get_connection()
    cursor = conn.cursor()

    try:
        # 1. Fetch open log
        cursor.execute("""
            SELECT log_id, zone_id, check_in_time
            FROM   parking_logs
            WHERE  log_id = ? AND check_out_time IS NULL
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
            SET    check_out_time   = ?,
                   duration_minutes = ?
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

        conn.commit()
        return {
            "success":          True,
            "log_id":           log_id,
            "check_out":        now.strftime("%Y-%m-%d %H:%M:%S"),
            "duration_minutes": duration_minutes,
        }

    except Exception as e:
        conn.rollback()
        return {"success": False, "error": str(e)}

    finally:
        conn.close()
