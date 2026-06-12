"""
ParkPredict — Admin Utilities
==============================
Administrative operations for managing parking zones.
Every action is recorded in admin_logs (audit trail).

Functions:
  update_zone_status(zone_id, status, by)  → manually set zone status
  reset_zone_slots(zone_id, by)            → emergency reset of a zone
  update_zone_capacity(zone_id, total, by) → change total slot count
  get_admin_logs(zone_id, limit)           → fetch audit trail
  get_capacity_history(zone_id, hours)     → slot history for charts
  get_full_audit(limit)                    → all admin actions
"""

from datetime import datetime
from db.connection import get_connection


def _log_action(cursor, zone_id, action, old_value, new_value, performed_by="admin"):
    """Insert a record into admin_logs — called by every admin function."""
    cursor.execute("""
        INSERT INTO admin_logs (zone_id, action, old_value, new_value, performed_by)
        VALUES (?, ?, ?, ?, ?)
    """, (zone_id, action, str(old_value), str(new_value), performed_by))


# ── ZONE STATUS ───────────────────────────────────────────────────────────

def update_zone_status(zone_id: int, status: str, performed_by: str = "admin") -> dict:
    """
    Manually override a zone's status.
    Records the change in admin_logs.

    Args:
      zone_id      : ID of zone to update
      status       : 'available' | 'full' | 'maintenance'
      performed_by : who made the change (default 'admin')
    """
    valid = ("available", "full", "maintenance")
    if status not in valid:
        return {"success": False, "error": f"Status must be one of: {valid}"}

    conn   = get_connection()
    cursor = conn.cursor()

    try:
        # Get old status first
        cursor.execute("SELECT status, zone_name FROM parking_zones WHERE zone_id = ?", (zone_id,))
        row = cursor.fetchone()
        if not row:
            return {"success": False, "error": f"Zone {zone_id} not found."}

        old_status = row["status"]

        cursor.execute("""
            UPDATE parking_zones
            SET    status = ?, last_updated = CURRENT_TIMESTAMP
            WHERE  zone_id = ?
        """, (status, zone_id))

        # Record in audit trail
        _log_action(cursor, zone_id,
                    action="STATUS_CHANGE",
                    old_value=old_status,
                    new_value=status,
                    performed_by=performed_by)

        conn.commit()
        return {
            "success":    True,
            "zone_id":    zone_id,
            "zone_name":  row["zone_name"],
            "old_status": old_status,
            "new_status": status,
        }

    except Exception as e:
        conn.rollback()
        return {"success": False, "error": str(e)}

    finally:
        conn.close()


# ── EMERGENCY RESET ───────────────────────────────────────────────────────

def reset_zone_slots(zone_id: int, performed_by: str = "admin") -> dict:
    """
    Emergency reset: restore available_slots to total_slots.
    Closes dangling logs and records the action in admin_logs.
    """
    conn   = get_connection()
    cursor = conn.cursor()

    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Get current state
        cursor.execute("""
            SELECT zone_name, available_slots, total_slots
            FROM   parking_zones WHERE zone_id = ?
        """, (zone_id,))
        row = cursor.fetchone()
        if not row:
            return {"success": False, "error": f"Zone {zone_id} not found."}

        old_available = row["available_slots"]

        # Count dangling logs
        cursor.execute("""
            SELECT COUNT(*) AS cnt FROM parking_logs
            WHERE zone_id = ? AND check_out_time IS NULL
        """, (zone_id,))
        dangling = cursor.fetchone()["cnt"]

        # Close dangling logs
        cursor.execute("""
            UPDATE parking_logs
            SET    check_out_time   = ?,
                   duration_minutes = CAST(
                       (julianday(?) - julianday(check_in_time)) * 1440 AS INTEGER
                   )
            WHERE  zone_id = ? AND check_out_time IS NULL
        """, (now, now, zone_id))

        # Reset slots
        cursor.execute("""
            UPDATE parking_zones
            SET    available_slots = total_slots,
                   status          = 'available',
                   last_updated    = CURRENT_TIMESTAMP
            WHERE  zone_id = ?
        """, (zone_id,))

        # Audit log
        _log_action(cursor, zone_id,
                    action="EMERGENCY_RESET",
                    old_value=f"available={old_available}, dangling={dangling}",
                    new_value=f"available={row['total_slots']}, dangling_closed={dangling}",
                    performed_by=performed_by)

        conn.commit()
        return {
            "success":         True,
            "zone_name":       row["zone_name"],
            "slots_restored":  row["total_slots"],
            "sessions_closed": dangling,
            "message":         f"Zone reset. {dangling} dangling session(s) closed.",
        }

    except Exception as e:
        conn.rollback()
        return {"success": False, "error": str(e)}

    finally:
        conn.close()


# ── CAPACITY MANAGEMENT ───────────────────────────────────────────────────

def update_zone_capacity(zone_id: int, new_total: int, performed_by: str = "admin") -> dict:
    """
    Update a zone's total slot count.
    Useful when new parking spaces are added or removed.
    Records the change in admin_logs.
    """
    if new_total <= 0:
        return {"success": False, "error": "total_slots must be greater than 0."}

    conn   = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT zone_name, total_slots, available_slots FROM parking_zones WHERE zone_id = ?
        """, (zone_id,))
        row = cursor.fetchone()
        if not row:
            return {"success": False, "error": f"Zone {zone_id} not found."}

        old_total = row["total_slots"]
        diff      = new_total - old_total
        new_avail = max(0, row["available_slots"] + diff)

        cursor.execute("""
            UPDATE parking_zones
            SET    total_slots     = ?,
                   available_slots = ?,
                   last_updated    = CURRENT_TIMESTAMP
            WHERE  zone_id = ?
        """, (new_total, new_avail, zone_id))

        _log_action(cursor, zone_id,
                    action="CAPACITY_UPDATE",
                    old_value=f"total={old_total}",
                    new_value=f"total={new_total}",
                    performed_by=performed_by)

        conn.commit()
        return {
            "success":       True,
            "zone_name":     row["zone_name"],
            "old_total":     old_total,
            "new_total":     new_total,
            "available_now": new_avail,
        }

    except Exception as e:
        conn.rollback()
        return {"success": False, "error": str(e)}

    finally:
        conn.close()


# ── AUDIT TRAIL ───────────────────────────────────────────────────────────

def get_admin_logs(zone_id: int = None, limit: int = 50) -> list:
    """
    Return admin action history.
    Pirai uses this for GET /api/admin/audit endpoint.

    Args:
      zone_id : optional filter by zone
      limit   : max rows to return (default 50)
    """
    conn   = get_connection()
    cursor = conn.cursor()

    if zone_id:
        cursor.execute("""
            SELECT al.action_id, al.zone_id, pz.zone_name,
                   al.action, al.old_value, al.new_value,
                   al.performed_by, al.action_time
            FROM   admin_logs al
            LEFT JOIN parking_zones pz ON al.zone_id = pz.zone_id
            WHERE  al.zone_id = ?
            ORDER  BY al.action_time DESC
            LIMIT  ?
        """, (zone_id, limit))
    else:
        cursor.execute("""
            SELECT al.action_id, al.zone_id, pz.zone_name,
                   al.action, al.old_value, al.new_value,
                   al.performed_by, al.action_time
            FROM   admin_logs al
            LEFT JOIN parking_zones pz ON al.zone_id = pz.zone_id
            ORDER  BY al.action_time DESC
            LIMIT  ?
        """, (limit,))

    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


# ── CAPACITY HISTORY ──────────────────────────────────────────────────────

def get_capacity_history(zone_id: int, hours: int = 24) -> list:
    """
    Return slot count snapshots for a zone over time.
    Used by Bala's real-time occupancy line chart on admin page.

    Args:
      zone_id : zone to query
      hours   : how many hours back (default 24)
    """
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT   recorded_at, available_slots, total_slots,
                 ROUND((1.0 - available_slots * 1.0 / total_slots) * 100, 1) AS occupancy_pct
        FROM     zone_capacity_history
        WHERE    zone_id = ?
          AND    recorded_at >= datetime('now', ?)
        ORDER BY recorded_at ASC
    """, (zone_id, f"-{hours} hours"))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_full_audit(limit: int = 100) -> list:
    """Return all admin actions across all zones — newest first."""
    return get_admin_logs(zone_id=None, limit=limit)