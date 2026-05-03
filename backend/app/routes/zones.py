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
    zones = get_all_zones()
    return jsonify({"success": True, "data": zones}), 200


@zones_bp.route("/<int:zone_id>", methods=["GET"])
def single_zone(zone_id):
    """Return live status of one zone."""
    zone = get_zone_by_id(zone_id)
    if not zone:
        return jsonify({"success": False, "error": "Zone not found."}), 404
    return jsonify({"success": True, "data": zone}), 200
