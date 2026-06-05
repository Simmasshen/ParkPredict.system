"""
ParkPredict — Zone Routes
==========================
Endpoints for reading parking zone status.
Used by Bala (Frontend) to power the parking map.

Endpoints:
  GET /api/zones/           → all zones (live status)
  GET /api/zones/<zone_id>  → single zone
"""

from flask import Blueprint, jsonify
from app.database import get_all_zones, get_zone_by_id

zones_bp = Blueprint("zones", __name__)


@zones_bp.route("/", methods=["GET"])
def all_zones():
    """Return live status of all parking zones."""
    try:
        zones = get_all_zones()
        return jsonify({"success": True, "count": len(zones), "data": zones}), 200
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to fetch zones: {str(e)}"}), 500


@zones_bp.route("/<int:zone_id>", methods=["GET"])
def single_zone(zone_id):
    """Return live status of one zone."""
    try:
        zone = get_zone_by_id(zone_id)
        if not zone:
            return jsonify({"success": False, "error": f"Zone {zone_id} not found."}), 404
        return jsonify({"success": True, "data": zone}), 200
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to fetch zone: {str(e)}"}), 500
