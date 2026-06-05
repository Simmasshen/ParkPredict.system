"""
ParkPredict — App Factory
==========================
Creates and configures the Flask application.
Registers all blueprints and global error handlers.
"""

from flask import Flask, jsonify
from flask_cors import CORS
from app.database              import init_db
from app.routes.zones          import zones_bp
from app.routes.parking        import parking_bp
from app.routes.analytics      import analytics_bp
from app.routes.admin          import admin_bp
from app.routes.recommendation import recommendation_bp
from app.routes.auth           import auth_bp
from app.services.auth         import create_users_table


def create_app():
    app = Flask(__name__)
    CORS(app)

    # Secret key required for session-based login/logout
    app.secret_key = "parkpredict_mmu_secret_2025"

    # ── Initialize database on startup ────────────────────────────────────
    with app.app_context():
        init_db()
        create_users_table()

    # ── Register Blueprints (clean routing structure) ─────────────────────
    app.register_blueprint(zones_bp,          url_prefix="/api/zones")
    app.register_blueprint(parking_bp,        url_prefix="/api/parking")
    app.register_blueprint(analytics_bp,      url_prefix="/api/analytics")
    app.register_blueprint(admin_bp,          url_prefix="/api/admin")
    app.register_blueprint(recommendation_bp, url_prefix="/api/recommendation")
    app.register_blueprint(auth_bp,           url_prefix="/api/auth")

    # ── Global Error Handlers ─────────────────────────────────────────────
    # These catch errors across ALL routes automatically.

    @app.errorhandler(400)
    def bad_request(e):
        """Missing or invalid request data."""
        return jsonify({"success": False, "error": "Bad request — check your request body or parameters."}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        """Not logged in or invalid credentials."""
        return jsonify({"success": False, "error": "Unauthorized — please log in first."}), 401

    @app.errorhandler(403)
    def forbidden(e):
        """No permission to access this resource."""
        return jsonify({"success": False, "error": "Forbidden — you don't have permission."}), 403

    @app.errorhandler(404)
    def not_found(e):
        """Route or resource does not exist."""
        return jsonify({"success": False, "error": "Not found — the endpoint or resource doesn't exist."}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        """Wrong HTTP method used (e.g. GET instead of POST)."""
        return jsonify({"success": False, "error": "Method not allowed — check if you used GET or POST correctly."}), 405

    @app.errorhandler(500)
    def internal_error(e):
        """Unexpected server-side error."""
        return jsonify({"success": False, "error": "Internal server error — something went wrong on the server."}), 500

    # ── Root route — API overview ─────────────────────────────────────────
    @app.route("/")
    def index():
        return jsonify({
            "message": "ParkPredict API is running ✅",
            "version": "2.0.0",
            "endpoints": {
                "Zones":          "GET  /api/zones/  |  GET  /api/zones/<zone_id>",
                "Parking":        "POST /api/parking/checkin  |  POST /api/parking/checkout",
                "Active":         "GET  /api/parking/active  |  GET  /api/parking/active/<zone_id>",
                "History":        "GET  /api/parking/history/<user_id>",
                "Analytics":      "GET  /api/analytics/summary  |  peak-hours  |  usage-trends  |  prediction  |  daily-stats  |  zone-comparison",
                "Admin":          "GET  /api/admin/stats  |  zones  |  logs  |  POST reset/<id>  |  status",
                "Recommendation": "GET  /api/recommendation/  |  ?user_id=S001",
                "Auth":           "POST /api/auth/register  |  login  |  logout  |  GET me  |  user-history",
            }
        }), 200

    return app
