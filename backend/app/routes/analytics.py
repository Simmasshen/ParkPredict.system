"""
ParkPredict — Analytics Routes
================================
Endpoints that return processed data for charts and predictions.
Uses Pandas to process raw data from Nitesh's database.

Endpoints
  GET /api/analytics/peak-hours          → peak hours chart data
  GET /api/analytics/prediction          → avg occupancy prediction data
  GET /api/analytics/summary             → overall summary stats
"""

from flask import Blueprint, jsonify, request
from app.database import get_peak_hours, get_prediction_data, get_all_zones
from app.services.prediction import predict_availability
from app.services.analytics  import build_peak_hours_summary, build_summary_stats

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/peak-hours", methods=["GET"])
def peak_hours():
    """
    Return peak hour data, processed by Pandas.
    Used by Bala (Frontend) to render bar charts.

    Query params:
      ?days=30   (optional, default 30)
    """
    days = request.args.get("days", default=30, type=int)
    raw  = get_peak_hours(days=days)
    data = build_peak_hours_summary(raw)
    return jsonify({"success": True, "data": data}), 200


@analytics_bp.route("/prediction", methods=["GET"])
def prediction():
    """
    Return parking availability prediction for all zones.
    Used by Bala (Frontend) to show probability of finding a spot.
    """
    raw    = get_prediction_data()
    zones  = get_all_zones()
    result = predict_availability(raw, zones)
    return jsonify({"success": True, "data": result}), 200


@analytics_bp.route("/summary", methods=["GET"])
def summary():
    """
    Return overall summary stats: total zones, total slots, occupancy rate.
    Used by Bala (Frontend) for the dashboard header.
    """
    zones = get_all_zones()
    stats = build_summary_stats(zones)
    return jsonify({"success": True, "data": stats}), 200
