"""
ParkPredict — App Factory
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
    CORS(app, supports_credentials=True, origins=["*"])

    app.secret_key = "parkpredict_mmu_secret_2025"

    with app.app_context():
        init_db()
        create_users_table()

    app.register_blueprint(zones_bp,          url_prefix="/api/zones")
    app.register_blueprint(parking_bp,        url_prefix="/api/parking")
    app.register_blueprint(analytics_bp,      url_prefix="/api/analytics")
    app.register_blueprint(admin_bp,          url_prefix="/api/admin")
    app.register_blueprint(recommendation_bp, url_prefix="/api/recommendation")
    app.register_blueprint(auth_bp,           url_prefix="/api/auth")

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"success": False, "error": "Bad request."}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"success": False, "error": "Unauthorized — please log in."}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"success": False, "error": "Forbidden."}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": "Not found."}), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"success": False, "error": "Internal server error."}), 500

    @app.route("/")
    def index():
        return jsonify({
            "message": "ParkPredict API is running ✅",
            "version": "2.1.0",
            "endpoints": {
                "Zones":          "GET  /api/zones/  |  GET  /api/zones/<zone_id>",
                "Parking":        "POST /api/parking/checkin  |  POST /api/parking/checkout",
                "Active":         "GET  /api/parking/active  |  /active/<zone_id>",
                "History":        "GET  /api/parking/history/<user_id>",
                "Analytics":      "GET  /api/analytics/summary  |  peak-hours  |  usage-trends  |  prediction  |  daily-stats  |  zone-comparison",
                "Admin":          "GET  /api/admin/stats  |  zones  |  logs  |  audit  |  POST reset/<id>  |  status",
                "Recommendation": "GET  /api/recommendation/  |  ?user_id=S001",
                "Auth":           "POST /api/auth/register  |  login  |  logout  |  GET me  |  user-history",
            }
        }), 200

    return app
