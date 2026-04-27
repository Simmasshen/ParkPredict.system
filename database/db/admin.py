"""
ParkPredict — Admin Utilities
==============================
Administrative operations for managing parking zones.
Intended for use by system admins, not regular users.

Functions:
  update_zone_status(zone_id, status)  → manually set zone status
  reset_zone_slots(zone_id)            → emergency reset of a zone
"""

from datetime import datetime
from db.connection import get_connection


def update_zone_status(zone_id: int, status: str) -> dict:
    """
    Manually override a zone's status.

    Args:
      zone_id : ID of the zone to update
      status  : 'available' | 'full' | 'maintenance'

    Returns:
      dict { success, zone_id, new_status }
      or   { success: False, error: "..." }
    """
    valid_statuses = ("available", "full", "maintenance")

    if status not in valid_statuses:
        return {"success": False,
                "error": f"Invalid status. Must be one of: {valid_statuses}"}

    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE parking_zones
        SET    status       = ?,
               last_updated = CURRENT_TIMESTAMP
        WHERE  zone_id = ?
    """, (status, zone_id))

    conn.commit()
    affected = cursor.rowcount
    conn.close()

    if affected == 0:
        return {"success": False, "error": f"Zone {zone_id} not found."}

    return {"success": True, "zone_id": zone_id, "new_status": status}


def reset_zone_slots(zone_id: int) -> dict:
    """
    Emergency reset: restore available_slots to total_slots.
    Also closes any dangling (un-checked-out) logs for that zone.

    Use when zone counts get out of sync due to app errors.

    Returns:
      dict { success, message }
      or   { success: False, error: "..." }
    """
    conn   = get_connection()
    cursor = conn.cursor()

    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Close dangling logs
        cursor.execute("""
            UPDATE parking_logs
            SET    check_out_time   = ?,
                   duration_minutes = CAST(
                       (julianday(?) - julianday(check_in_time)) * 1440 AS INTEGER
                   )
            WHERE  zone_id = ? AND check_out_time IS NULL
        """, (now, now, zone_id))

        # Reset available_slots to total_slots
        cursor.execute("""
            UPDATE parking_zones
            SET    available_slots = total_slots,
                   status          = 'available',
                   last_updated    = CURRENT_TIMESTAMP
            WHERE  zone_id = ?
        """, (zone_id,))

        conn.commit()
        return {"success": True,
                "message": f"Zone {zone_id} reset successfully."}

    except Exception as e:
        conn.rollback()
        return {"success": False, "error": str(e)}

    finally:
        conn.close()
