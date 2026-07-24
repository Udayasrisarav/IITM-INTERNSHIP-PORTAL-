from flask import Blueprint, g, jsonify, request

from middleware.auth_middleware import jwt_required_custom
from services.application_service import (
    create_application,
    get_application,
    update_application,
    submit_application,
)

application_bp = Blueprint("application", __name__, url_prefix="/api/v1/applications")


def _serialize_application(application) -> dict:
    return {
        "id": application.id,
        "profile_id": application.profile_id,
        "schedule_id": application.schedule_id,
        "application_number": application.application_number,
        "referred_by": application.referred_by,
        "referred_from": application.referred_from,
        "status": application.status,
        "submitted_at": application.submitted_at.isoformat() if application.submitted_at else None,
        "created_at": application.created_at.isoformat() if application.created_at else None,
        "updated_at": application.updated_at.isoformat() if application.updated_at else None,
    }


@application_bp.route("/", methods=["POST"])
@jwt_required_custom
def create_application_route():
    current_user = getattr(g, "current_user", None)
    data = request.get_json(silent=True) or {}
    application, error, status_code = create_application(current_user.id, data)
    if error:
        return jsonify({"error": error}), status_code
    return jsonify(_serialize_application(application)), status_code


@application_bp.route("/", methods=["GET"])
@jwt_required_custom
def list_applications_route():
    current_user = getattr(g, "current_user", None)
    applications, error, status_code = get_application(current_user.id)
    if error:
        return jsonify({"error": error}), status_code
    return jsonify([_serialize_application(app) for app in applications]), status_code


@application_bp.route("/<int:application_id>", methods=["GET"])
@jwt_required_custom
def get_application_route(application_id):
    current_user = getattr(g, "current_user", None)
    application, error, status_code = get_application(current_user.id, application_id)
    if error:
        return jsonify({"error": error}), status_code
    return jsonify(_serialize_application(application)), status_code


@application_bp.route("/<int:application_id>", methods=["PUT"])
@jwt_required_custom
def update_application_route(application_id):
    current_user = getattr(g, "current_user", None)
    data = request.get_json(silent=True) or {}
    application, error, status_code = update_application(current_user.id, application_id, data)
    if error:
        return jsonify({"error": error}), status_code
    return jsonify(_serialize_application(application)), status_code


@application_bp.route("/<int:application_id>/submit", methods=["POST"])
@jwt_required_custom
def submit_application_route(application_id):
    current_user = getattr(g, "current_user", None)
    application, error, status_code = submit_application(current_user.id, application_id)
    if error:
        return jsonify({"error": error}), status_code
    return jsonify(_serialize_application(application)), status_code
