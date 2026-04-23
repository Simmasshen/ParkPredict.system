from flask import Blueprint, request, jsonify

parking_bp = Blueprint('parking', __name__)

@parking_bp.route('/checkin', methods=['POST'])
def checkin():
    return jsonify({"message": "Checked in"})

@parking_bp.route('/checkout', methods=['POST'])
def checkout():
    return jsonify({"message": "Checked out"})

@parking_bp.route('/parking-status', methods=['GET'])
def status():
    return jsonify({"zones": []})