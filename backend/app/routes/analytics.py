"""
ParkPredict — Analytics Routes

Endpoints:
  GET /api/analytics/summary          → overall dashboard stats
  GET /api/analytics/peak-hours       → peak hours by day & hour
  GET /api/analytics/usage-trends     → zone usage trends over time
  GET /api/analytics/prediction       → availability probability per zone
  GET /api/analytics/daily-stats      → today's statistics
  GET /api/analytics/zone-comparison  → side-by-side zone comparison
"""

from flask import Blueprint, jsonify, request
from app.database import (
    get_peak_hours,
    get_prediction_data,
    get_all_zones,
    get_daily_stats,           # FIX: was missing from original
)
from app.services.prediction import predict_availability
from app.services.analytics  import (
    build_peak_hours_summary,
    build_summary_stats,
    build_usage_trends,
    build_zone_comparison,
)

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/summary", methods=["GET"])
def summary():
    """Overall dashboard stats."""
    zones = get_all_zones()
    stats = build_summary_stats(zones)
    return jsonify({"success": True, "data": stats}), 200


@analytics_bp.route("/peak-hours", methods=["GET"])
def peak_hours():
    """Peak hour data for bar charts."""
    days    = request.args.get("days",    default=30,   type=int)
    zone_id = request.args.get("zone_id", default=None, type=int)
    raw  = get_peak_hours(days=days)
    data = build_peak_hours_summary(raw, zone_id=zone_id)
    return jsonify({"success": True, "data": data}), 200


@analytics_bp.route("/usage-trends", methods=["GET"])
def usage_trends():
    """Zone usage trends over time."""
    days = request.args.get("days", default=30, type=int)
    raw  = get_peak_hours(days=days)
    data = build_usage_trends(raw)
    return jsonify({"success": True, "data": data}), 200


@analytics_bp.route("/prediction", methods=["GET"])
def prediction():
    """Availability probability per zone."""
    raw    = get_prediction_data()
    zones  = get_all_zones()
    result = predict_availability(raw, zones)
    return jsonify({"success": True, "data": result}), 200


@analytics_bp.route("/daily-stats", methods=["GET"])
def daily_stats():
    """Today's stats — check-ins, check-outs, avg duration, busiest zone."""
    date = request.args.get("date", default=None, type=str)
    data = get_daily_stats(date=date)
    return jsonify({"success": True, "data": data}), 200


@analytics_bp.route("/zone-comparison", methods=["GET"])
def zone_comparison():
    """Side-by-side zone comparison."""
    raw   = get_prediction_data()
    zones = get_all_zones()
    data  = build_zone_comparison(raw, zones)
    return jsonify({"success": True, "data": data}), 200
