from flask import Blueprint, request, jsonify, g
from services.auth_service import login_user, get_user_details, google_oauth_authenticate
from middleware.auth_middleware import jwt_required_custom

auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    POST /api/v1/auth/login
    Request payload: {"username": "...", "password": "..."}
    Response payload: {"access_token": "...", "role": "...", "user_id": ...}
    """
    data = request.get_json(silent=True) or {}
    identifier = data.get("username") or data.get("email")
    password = data.get("password")

    result, error_msg, status_code = login_user(identifier, password)
    if error_msg:
        return jsonify({"error": error_msg}), status_code

    return jsonify(result), status_code


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """
    POST /api/v1/auth/logout
    Response payload: {"message": "Logged out successfully"}
    """
    return jsonify({"message": "Logged out successfully"}), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required_custom
def get_current_user():
    """
    GET /api/v1/auth/me
    Returns current authenticated user profile.
    Response payload: {"id": ..., "full_name": "...", "email": "...", "role": "...", "is_active": true}
    """
    current_user = getattr(g, "current_user", None)
    if not current_user:
        return jsonify({"error": "User context not found"}), 401

    user_info = get_user_details(current_user)
    return jsonify(user_info), 200


@auth_bp.route("/google", methods=["POST"])
def google_login():
    """
    POST /api/v1/auth/google
    Structure & integration-ready endpoint for Google OAuth single sign-on.
    """
    data = request.get_json(silent=True) or {}
    id_token = data.get("id_token")

    result, error_msg, status_code = google_oauth_authenticate(id_token)
    if error_msg:
        return jsonify({"error": error_msg}), status_code

    return jsonify(result), status_code
