"""
ParkPredict — Parking Routes
==============================
Endpoints for check-in and check-out actions.

Endpoints:
  POST /api/parking/checkin              → user checks in
  POST /api/parking/checkout             → user checks out
  GET  /api/parking/active               → all active sessions
  GET  /api/parking/active/<zone_id>     → active sessions in one zone
  GET  /api/parking/history/<user_id>    → parking history for a user
"""

from flask import Blueprint, request, jsonify
from app.database import check_in, check_out, get_active_logs, get_logs_by_user

parking_bp = Blueprint("parking", __name__)


@parking_bp.route("/checkin", methods=["POST"])
def checkin():
    """
    Check in a user to a parking zone.

    Request body (JSON):
      { "zone_id": 1, "user_id": "S001", "vehicle_plate": "WXX1234" }

    vehicle_plate is optional.
    """
    try:
        data = request.get_json()

        # ── Validate request body ─────────────────────────────────────────
        if not data:
            return jsonify({"success": False,
                            "error": "Request body is required. Send JSON with zone_id and user_id."}), 400

        zone_id       = data.get("zone_id")
        user_id       = data.get("user_id")
        vehicle_plate = data.get("vehicle_plate")

        if not zone_id:
            return jsonify({"success": False, "error": "zone_id is required."}), 400
        if not user_id:
            return jsonify({"success": False, "error": "user_id is required."}), 400
        if not isinstance(zone_id, int):
            return jsonify({"success": False, "error": "zone_id must be a number."}), 400

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
            return jsonify({"success": False,
                            "error": "Request body is required. Send JSON with log_id."}), 400

        log_id = data.get("log_id")

        if not log_id:
            return jsonify({"success": False, "error": "log_id is required."}), 400
        if not isinstance(log_id, int):
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
