"""
ParkPredict — Recommendation Route
=====================================
Smart parking recommendation endpoint.
Fetches live + historical data and returns the single best zone.

Endpoint:
  GET /api/recommendation/             → best zone right now
  GET /api/recommendation/?user_id=S001 → best zone for a specific user
"""

from flask import Blueprint, jsonify, request
from app.database import get_all_zones, get_prediction_data, get_logs_by_user
from app.services.recommendation import get_best_zone

recommendation_bp = Blueprint("recommendation", __name__)


@recommendation_bp.route("/", methods=["GET"])
def recommend():
    """
    Return the single best parking zone to go to right now.

    Optional query param:
      ?user_id=S001  — if provided, avoids zones the user just left

    Response:
      {
        "success": true,
        "recommended_zone": { zone_id, zone_name, location,
                               available_slots, total_slots,
                               probability, reason },
        "all_zones_ranked": [ ... all zones sorted best to worst ... ]
      }
    """
    user_id = request.args.get("user_id", default=None)

    # Fetch live zone data + historical prediction data
    zones      = get_all_zones()
    historical = get_prediction_data()

    # Get user's recent history to avoid recommending zones they just left
    recent_zones = []
    if user_id:
        history = get_logs_by_user(user_id=user_id, limit=3)
        recent_zones = [h["zone_id"] for h in history]

    result = get_best_zone(zones, historical, recent_zones)

    return jsonify({"success": True, **result}), 200
