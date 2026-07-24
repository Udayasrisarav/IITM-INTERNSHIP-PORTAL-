from datetime import datetime

from database import db
from models import Application, Profile, User

ALLOWED_CREATE_FIELDS = {"referred_by", "referred_from", "schedule_id"}
ALLOWED_UPDATE_FIELDS = {"referred_by", "referred_from", "schedule_id"}


def _generate_application_number() -> str:
    year = datetime.utcnow().year
    prefix = f"IITM-{year}-%"
    last_application = (
        Application.query.filter(Application.application_number.like(prefix))
        .order_by(Application.id.desc())
        .first()
    )

    if not last_application or not last_application.application_number:
        return f"IITM-{year}-0001"

    try:
        last_suffix = int(last_application.application_number.split("-")[-1])
    except (ValueError, IndexError):
        return f"IITM-{year}-0001"

    return f"IITM-{year}-{last_suffix + 1:04d}"


def _build_application_data(data: dict, *, for_update: bool = False) -> dict:
    allowed_fields = ALLOWED_UPDATE_FIELDS if for_update else ALLOWED_CREATE_FIELDS
    application_data = {}

    for field in allowed_fields:
        if field in data:
            application_data[field] = data[field]

    return application_data


def create_application(user_id: int, data: dict):
    user = User.query.get(user_id)
    if not user:
        return None, "User not found", 404

    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile:
        return None, "Profile must exist before creating an application", 400

    try:
        application_data = _build_application_data(data, for_update=False)
    except Exception as exc:
        return None, str(exc), 400

    application = Application(
        profile_id=profile.id,
        application_number=_generate_application_number(),
        status="Draft",
        **application_data,
    )
    db.session.add(application)
    db.session.commit()
    return application, None, 201


def get_application(user_id: int, application_id: int | None = None):
    user = User.query.get(user_id)
    if not user:
        return None, "User not found", 404

    if application_id is None:
        applications = Application.query.join(Profile).filter(Profile.user_id == user_id).all()
        return applications, None, 200

    application = Application.query.get(application_id)
    if not application:
        return None, "Application not found", 404

    profile = Profile.query.get(application.profile_id)
    if not profile or profile.user_id != user_id:
        return None, "Access denied. Applicants can only view their own applications", 403

    return application, None, 200


def update_application(user_id: int, application_id: int, data: dict):
    application, error, status_code = get_application(user_id, application_id)
    if error:
        return None, error, status_code

    if application.status != "Draft":
        return None, "Applications can only be updated while in Draft status", 400

    try:
        application_data = _build_application_data(data, for_update=True)
    except Exception as exc:
        return None, str(exc), 400

    for field, value in application_data.items():
        setattr(application, field, value)

    db.session.commit()
    return application, None, 200


def submit_application(user_id: int, application_id: int):
    application, error, status_code = get_application(user_id, application_id)
    if error:
        return None, error, status_code

    if application.status != "Draft":
        return None, "Application is already submitted or not in Draft status", 400

    application.status = "Submitted"
    application.submitted_at = datetime.utcnow()
    db.session.commit()
    return application, None, 200
