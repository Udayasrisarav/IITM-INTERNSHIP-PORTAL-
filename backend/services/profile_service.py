from datetime import datetime, date

from database import db
from models import User, Profile

PROFILE_FIELDS = {
    "full_name",
    "mobile_number",
    "gender",
    "date_of_birth",
    "address",
    "college_name",
    "department",
    "register_number",
    "year_of_study",
    "skills",
    "area_of_interest",
}


def _parse_date_of_birth(value):
    if value is None:
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, str) and value.strip() == "":
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except Exception:
        raise ValueError("Invalid date format for date_of_birth. Expected YYYY-MM-DD")


def _build_profile_data(data: dict) -> dict:
    profile_data = {}
    for field in PROFILE_FIELDS:
        if field in data:
            if field == "date_of_birth":
                profile_data[field] = _parse_date_of_birth(data[field])
            else:
                profile_data[field] = data[field]
    return profile_data


def create_profile(user_id: int, data: dict):
    if not data or not data.get("full_name"):
        return None, "full_name is required", 400

    user = User.query.get(user_id)
    if not user:
        return None, "User not found", 404

    if user.profile:
        return None, "Profile already exists for this user", 409

    try:
        profile_data = _build_profile_data(data)
    except ValueError as exc:
        return None, str(exc), 400

    profile = Profile(user_id=user_id, **profile_data)
    db.session.add(profile)
    db.session.commit()
    return profile, None, 201


def get_profile(user_id: int):
    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile:
        return None, "Profile not found", 404
    return profile, None, 200


def update_profile(user_id: int, data: dict):
    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile:
        return None, "Profile not found", 404

    if "full_name" in data and not data.get("full_name"):
        return None, "full_name cannot be empty", 400

    try:
        profile_data = _build_profile_data(data)
    except ValueError as exc:
        return None, str(exc), 400

    for field, value in profile_data.items():
        setattr(profile, field, value)

    db.session.commit()
    return profile, None, 200
