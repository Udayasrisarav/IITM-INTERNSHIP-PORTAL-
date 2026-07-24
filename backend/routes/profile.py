from flask import Blueprint, request, jsonify, g
from middleware.auth_middleware import jwt_required_custom
from services.profile_service import create_profile, get_profile, update_profile
from models import Profile

profile_bp = Blueprint("profile", __name__, url_prefix="/api/v1")


def _is_superadmin(user) -> bool:
    return (
        user
        and getattr(user, "role_mapping", None)
        and getattr(user.role_mapping, "role", None)
        and user.role_mapping.role.role_name == "SuperAdmin"
    )


def _serialize_profile(profile: Profile) -> dict:
    return {
        "id": profile.id,
        "user_id": profile.user_id,
        "full_name": profile.full_name,
        "mobile_number": profile.mobile_number,
        "gender": profile.gender,
        "date_of_birth": profile.date_of_birth.isoformat() if profile.date_of_birth else None,
        "address": profile.address,
        "college_name": profile.college_name,
        "department": profile.department,
        "register_number": profile.register_number,
        "year_of_study": profile.year_of_study,
        "skills": profile.skills,
        "area_of_interest": profile.area_of_interest,
        "created_at": profile.created_at.isoformat() if profile.created_at else None,
        "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
    }


@profile_bp.route("/profile", methods=["POST"])
@jwt_required_custom
def create_profile_route():
    current_user = getattr(g, "current_user", None)
    data = request.get_json(silent=True) or {}
    profile, error, status_code = create_profile(current_user.id, data)
    if error:
        return jsonify({"error": error}), status_code
    return jsonify(_serialize_profile(profile)), status_code


@profile_bp.route("/profile", methods=["GET"])
@jwt_required_custom
def get_profile_route():
    current_user = getattr(g, "current_user", None)
    requested_user_id = request.args.get("user_id", type=int)
    if requested_user_id and requested_user_id != current_user.id:
        if not _is_superadmin(current_user):
            return jsonify({"error": "Access denied. Only the profile owner or SuperAdmin can view this profile."}), 403
        target_user_id = requested_user_id
    else:
        target_user_id = current_user.id

    profile, error, status_code = get_profile(target_user_id)
    if error:
        return jsonify({"error": error}), status_code
    return jsonify(_serialize_profile(profile)), status_code


@profile_bp.route("/profile", methods=["PUT"])
@jwt_required_custom
def update_profile_route():
    current_user = getattr(g, "current_user", None)
    data = request.get_json(silent=True) or {}
    profile, error, status_code = update_profile(current_user.id, data)
    if error:
        return jsonify({"error": error}), status_code
    return jsonify(_serialize_profile(profile)), status_code
