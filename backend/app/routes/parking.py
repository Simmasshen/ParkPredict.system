"""
ParkPredict — Parking Routes
Endpoints for check-in and check-out actions.

Endpoints:
  POST /api/parking/checkin              → user checks in
  POST /api/parking/checkout             → user checks out
  GET  /api/parking/active               → all active sessions
  GET  /api/parking/active/<zone_id>     → active sessions in one zone
  GET  /api/parking/history/<user_id>    → parking history for a user
"""

from flask import Blueprint, request, jsonify
from app.database import (
    check_in, check_out, get_active_logs,
    get_logs_by_user, get_all_zones,
)

parking_bp = Blueprint("parking", __name__)

# Map zone name strings to zone IDs (matching seed data order)
ZONE_NAME_MAP = {
    "1": 1, "2": 2, "3": 3,
    "A": 1, "B": 2, "C": 3,
    "FCI": 1, "FOM": 2, "DTC": 3,
    "Zone A": 1, "Zone B": 2, "Zone C": 3,
}


def _resolve_zone_id(value) -> int | None:
    """Resolve zone_id from int, string number, or zone name."""
    if value is None:
        return None
    if isinstance(value, int):
        return value
    # Try int cast first
    try:
        return int(value)
    except (ValueError, TypeError):
        pass
    # Try name mapping
    key = str(value).strip().upper()
    return ZONE_NAME_MAP.get(key)


@parking_bp.route("/checkin", methods=["POST"])
def checkin():
    """
    Check in a user to a parking zone.

    Request body (JSON):
      { "zone_id": 1, "user_id": "S001", "vehicle_plate": "WXX1234" }
    OR frontend format:
      { "zone": "FCI", "student_id": "S001", "plate": "WXX1234", "vehicle_type": "Car" }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Request body is required."}), 400

        # Support both backend field names and frontend field names
        zone_raw      = data.get("zone_id") or data.get("zone")
        user_id       = data.get("user_id") or data.get("student_id")
        vehicle_plate = data.get("vehicle_plate") or data.get("plate")

        if not zone_raw:
            return jsonify({"success": False, "error": "zone_id (or zone) is required."}), 400
        if not user_id:
            return jsonify({"success": False, "error": "user_id (or student_id) is required."}), 400

        zone_id = _resolve_zone_id(zone_raw)
        if zone_id is None:
            return jsonify({"success": False,
                            "error": f"Unknown zone '{zone_raw}'. Use zone_id 1–3 or names FCI/FOM/DTC."}), 400

        result      = check_in(zone_id=zone_id, user_id=str(user_id), vehicle_plate=vehicle_plate)
        status_code = 200 if result["success"] else 400
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({"success": False, "error": f"Check-in failed: {str(e)}"}), 500


@parking_bp.route("/checkout", methods=["POST"])
def checkout():
    """
    Check out a user from a parking zone.

    Request body (JSON):
      { "log_id": 5 }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Request body is required."}), 400

        log_id = data.get("log_id")
        if not log_id:
            return jsonify({"success": False, "error": "log_id is required."}), 400
        if not isinstance(log_id, int):
            try:
                log_id = int(log_id)
            except (ValueError, TypeError):
                return jsonify({"success": False, "error": "log_id must be a number."}), 400

        result      = check_out(log_id=log_id)
        status_code = 200 if result["success"] else 400
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({"success": False, "error": f"Check-out failed: {str(e)}"}), 500


@parking_bp.route("/active", methods=["GET"])
def active_sessions():
    """Return all currently-parked vehicles across all zones."""
    try:
        logs = get_active_logs()
        return jsonify({"success": True, "count": len(logs), "data": logs}), 200
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to fetch active sessions: {str(e)}"}), 500


@parking_bp.route("/active/<int:zone_id>", methods=["GET"])
def active_sessions_by_zone(zone_id):
    """Return currently-parked vehicles in a specific zone."""
    try:
        logs = get_active_logs(zone_id=zone_id)
        return jsonify({"success": True, "count": len(logs), "data": logs}), 200
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to fetch sessions: {str(e)}"}), 500


@parking_bp.route("/history/<string:user_id>", methods=["GET"])
def user_history(user_id):
    """Return parking history for a specific user."""
    try:
        limit = request.args.get("limit", default=20, type=int)
        logs  = get_logs_by_user(user_id=user_id, limit=limit)
        return jsonify({"success": True, "user_id": user_id,
                        "count": len(logs), "data": logs}), 200
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to fetch history: {str(e)}"}), 500
