from flask import Blueprint, request, jsonify

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    return jsonify({"message": "User registered", "data": data})

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    return jsonify({"message": "User logged in", "data": data})

@auth_bp.route('/user-history', methods=['GET'])
def history():
    return jsonify({"history": []})