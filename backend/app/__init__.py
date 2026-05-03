"""
ParkPredict — App Factory
==========================
Creates and configures the Flask application.
"""

from flask import Flask
from flask_cors import CORS
from app.database         import init_db
from app.routes.zones     import zones_bp
from app.routes.parking   import parking_bp
from app.routes.analytics import analytics_bp


def create_app():
    app = Flask(__name__)
    CORS(app)   # allows Bala's frontend to call this backend

    # ── Initialize database on startup ────────────────────────────────────
    with app.app_context():
        init_db()

    # ── Register Blueprints ───────────────────────────────────────────────
    app.register_blueprint(zones_bp,     url_prefix="/api/zones")
    app.register_blueprint(parking_bp,   url_prefix="/api/parking")
    app.register_blueprint(analytics_bp, url_prefix="/api/analytics")

    # ── Root route ────────────────────────────────────────────────────────
    @app.route("/")
    def index():
        return {
            "message": "ParkPredict API is running",
            "version": "1.0.0",
            "endpoints": {
                "GET  /api/zones/":                    "All zones with live status",
                "GET  /api/zones/<zone_id>":           "Single zone",
                "POST /api/parking/checkin":           "Check in  { zone_id, user_id, vehicle_plate }",
                "POST /api/parking/checkout":          "Check out { log_id }",
                "GET  /api/parking/active":            "All active sessions",
                "GET  /api/parking/active/<zone_id>":  "Active sessions by zone",
                "GET  /api/parking/history/<user_id>": "User parking history",
                "GET  /api/analytics/peak-hours":      "Peak hour chart data",
                "GET  /api/analytics/prediction":      "Availability prediction",
                "GET  /api/analytics/summary":         "Dashboard summary stats",
            }
        }

    return app
