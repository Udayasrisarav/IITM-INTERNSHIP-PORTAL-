from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)

@health_bp.route("/health", methods=["GET"])
def health_check():
    """System health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "Internship Management Portal Backend API",
        "version": "1.0.0"
    }), 200

@health_bp.route("/api/v1/health", methods=["GET"])
def api_v1_health():
    """API V1 health check endpoint."""
    return jsonify({
        "status": "healthy",
        "api_version": "v1",
        "service": "Internship Management Portal Backend API"
    }), 200
