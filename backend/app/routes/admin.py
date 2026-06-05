"""
ParkPredict — Admin Routes
============================
Endpoints for the admin dashboard.
Used by Bala's admin.html page.

Endpoints:
  GET  /api/admin/stats              → today's stats summary
  GET  /api/admin/zones              → all zones with full details
  GET  /api/admin/logs               → all active parking sessions
  POST /api/admin/reset/<zone_id>    → emergency reset a zone
  POST /api/admin/status             → update a zone's status
"""

from flask import Blueprint, jsonify, request
from app.database import (
    get_all_zones,
    get_active_logs,
    update_zone_status,
    reset_zone_slots,
)
from datetime import datetime

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/stats", methods=["GET"])
def admin_stats():
    """
    Return summary stats for the admin dashboard header.
    Total zones, total slots, occupied slots, occupancy rate.
    """
    zones = get_all_zones()

    total_slots     = sum(z["total_slots"]     for z in zones)
    available_slots = sum(z["available_slots"] for z in zones)
    occupied_slots  = total_slots - available_slots
    occupancy_rate  = round((occupied_slots / total_slots) * 100, 1) if total_slots > 0 else 0
    full_zones      = sum(1 for z in zones if z["status"] == "full")
    maintenance     = sum(1 for z in zones if z["status"] == "maintenance")

    return jsonify({
        "success": True,
        "data": {
            "total_zones":            len(zones),
            "total_slots":            total_slots,
            "available_slots":        available_slots,
            "occupied_slots":         occupied_slots,
            "occupancy_rate_percent": occupancy_rate,
            "full_zones":             full_zones,
            "maintenance_zones":      maintenance,
            "last_updated":           datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    }), 200


@admin_bp.route("/zones", methods=["GET"])
def admin_zones():
    """Return all zones with full details for the admin table."""
    zones = get_all_zones()
    return jsonify({"success": True, "data": zones}), 200


@admin_bp.route("/logs", methods=["GET"])
def admin_logs():
    """Return all currently active parking sessions."""
    logs = get_active_logs()
    return jsonify({"success": True, "data": logs, "count": len(logs)}), 200


@admin_bp.route("/reset/<int:zone_id>", methods=["POST"])
def admin_reset(zone_id):
    """
    Emergency reset — restore a zone's slots to full capacity.
    Also closes any dangling check-in logs for that zone.
    """
    result = reset_zone_slots(zone_id)
    status_code = 200 if result["success"] else 400
    return jsonify(result), status_code


@admin_bp.route("/status", methods=["POST"])
def admin_status():
    """
    Update a zone's status manually.

    Request body (JSON):
      { "zone_id": 1, "status": "maintenance" }

    status options: "available" | "full" | "maintenance"
    """
    data    = request.get_json()
    zone_id = data.get("zone_id")
    status  = data.get("status")

    if not zone_id or not status:
        return jsonify({"success": False,
                        "error": "zone_id and status are required."}), 400

    result = update_zone_status(zone_id=zone_id, status=status)
    status_code = 200 if result["success"] else 400
    return jsonify(result), status_code
