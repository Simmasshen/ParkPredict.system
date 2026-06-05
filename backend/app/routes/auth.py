"""
ParkPredict — Auth & User Routes
===================================
User account API — register, login, logout, history.
Uses Flask session for authentication (no extra libraries needed).

Endpoints:
  POST /api/auth/register        → create new account
  POST /api/auth/login           → login
  POST /api/auth/logout          → logout
  GET  /api/auth/me              → get current logged-in user
  GET  /api/auth/user-history    → parking history for logged-in user
"""

import hashlib
import os
from datetime import datetime
from flask import Blueprint, jsonify, request, session
from app.database import get_logs_by_user
from app.services.auth import (
    create_user,
    find_user_by_username,
    find_user_by_id,
    hash_password,
    verify_password,
)

auth_bp = Blueprint("auth", __name__)


# ── REGISTER ──────────────────────────────────────────────────────────────

@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Create a new user account.

    Request body (JSON):
      { "username": "nitesh01", "password": "mypassword",
        "student_id": "S001", "email": "nitesh@mmu.edu.my" }

    student_id and email are optional.
    """
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "Request body required."}), 400

    username   = data.get("username", "").strip()
    password   = data.get("password", "")
    student_id = data.get("student_id", "").strip()
    email      = data.get("email", "").strip()

    if not username or not password:
        return jsonify({"success": False,
                        "error": "username and password are required."}), 400

    if len(password) < 6:
        return jsonify({"success": False,
                        "error": "Password must be at least 6 characters."}), 400

    # Check if username already exists
    if find_user_by_username(username):
        return jsonify({"success": False,
                        "error": "Username already taken."}), 409

    # Create user
    user_id = create_user(
        username=username,
        password_hash=hash_password(password),
        student_id=student_id,
        email=email
    )

    return jsonify({
        "success":  True,
        "message":  "Account created successfully.",
        "user_id":  user_id,
        "username": username,
    }), 201


# ── LOGIN ─────────────────────────────────────────────────────────────────

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login with username and password.

    Request body (JSON):
      { "username": "nitesh01", "password": "mypassword" }
    """
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "Request body required."}), 400

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"success": False,
                        "error": "username and password are required."}), 400

    user = find_user_by_username(username)

    if not user or not verify_password(password, user["password_hash"]):
        return jsonify({"success": False,
                        "error": "Invalid username or password."}), 401

    # Save user in session
    session["user_id"]  = user["user_id"]
    session["username"] = user["username"]

    return jsonify({
        "success":    True,
        "message":    f"Welcome back, {user['username']}!",
        "user_id":    user["user_id"],
        "username":   user["username"],
        "student_id": user.get("student_id", ""),
    }), 200


# ── LOGOUT ────────────────────────────────────────────────────────────────

@auth_bp.route("/logout", methods=["POST"])
def logout():
    """Clear the session and log out the user."""
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully."}), 200


# ── CURRENT USER ──────────────────────────────────────────────────────────

@auth_bp.route("/me", methods=["GET"])
def me():
    """
    Return the currently logged-in user's info.
    Returns 401 if not logged in.
    """
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Not logged in."}), 401

    user = find_user_by_id(user_id)
    if not user:
        return jsonify({"success": False, "error": "User not found."}), 404

    return jsonify({
        "success":    True,
        "user_id":    user["user_id"],
        "username":   user["username"],
        "student_id": user.get("student_id", ""),
        "email":      user.get("email", ""),
        "created_at": user.get("created_at", ""),
    }), 200


# ── USER PARKING HISTORY ──────────────────────────────────────────────────

@auth_bp.route("/user-history", methods=["GET"])
def user_history():
    """
    Return parking history for the currently logged-in user.
    Links users with parking_logs using their student_id.

    Query params:
      ?limit=20  (optional, default 20)
    """
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Not logged in."}), 401

    user = find_user_by_id(user_id)
    if not user:
        return jsonify({"success": False, "error": "User not found."}), 404

    limit      = request.args.get("limit", default=20, type=int)
    student_id = user.get("student_id") or user["username"]

    # Fetch logs from Nitesh's database using student_id as user_id
    logs = get_logs_by_user(user_id=student_id, limit=limit)

    return jsonify({
        "success":  True,
        "username": user["username"],
        "user_id":  student_id,
        "count":    len(logs),
        "data":     logs,
    }), 200
